#!/usr/bin/env python3
"""
live_transcriber.py — Transcripteur Live Audio GPU Whisper en tâche de fond.

Fonctionnalités :
- Capture audio double flux temps réel (Microphone physique + Sortie PC / Discord via WASAPI Loopback).
- Synchronisation non-bloquante par callbacks haute priorité (PyAudioWPatch).
- Fail-Fast et tolérance de panne : si la sortie loopback est inactive, silencieuse ou déconnectée,
  le microphone d'Henri continue d'enregistrer et de transcrire de façon 100% ininterrompue.
- Détection de voix / silences avec buffer dynamique, seuil RMS et VAD Silero (Faster-Whisper).
- Filtrage des hallucinations Whisper classiques sur silences ou bruits de fond.
- Inférence locale Faster-Whisper GPU CUDA FP16 (avec fallback int8_float16 puis CPU).
- Résolution automatique des DLL NVIDIA CUDA sous Windows.
- Écriture append-only continue avec flush() et os.fsync() dans live_session.md.
- Serveur HTTP léger intégré (port 3055 par défaut) avec endpoint GET /recent?minutes=10 et /status.
- Journalisation continue dans la console et dans transcriber.log.
"""

import argparse
import collections
from datetime import datetime
import http.server
import json
import logging
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path
import queue
import sys
import threading
import time
from typing import Optional, Tuple
from urllib.parse import parse_qs, urlparse

import numpy as np

# ---------------------------------------------------------------------------
# Résolution automatique des DLL CUDA sous Windows
# ---------------------------------------------------------------------------
def setup_cuda_dlls():
    """Détecte et enregistre les répertoires bin des bibliothèques NVIDIA pip."""
    if sys.platform != "win32":
        return

    added = []
    py_prefix = Path(sys.prefix)
    nvidia_base = py_prefix / "Lib" / "site-packages" / "nvidia"
    if nvidia_base.exists():
        for sub in nvidia_base.iterdir():
            bin_dir = sub / "bin"
            if bin_dir.exists():
                try:
                    os.add_dll_directory(str(bin_dir))
                    added.append(str(bin_dir))
                except Exception:
                    pass

    if added:
        os.environ["PATH"] = os.pathsep.join(added) + os.pathsep + os.environ.get("PATH", "")


setup_cuda_dlls()

# Imports conditionnels
try:
    import sounddevice as sd
except ImportError as err:
    sys.stderr.write("Le package 'sounddevice' est requis : pip install sounddevice\n")
    raise err

try:
    import pyaudiowpatch as pyaudio
    HAS_PYAUDIOWPATCH = True
except ImportError:
    HAS_PYAUDIOWPATCH = False

try:
    from faster_whisper import WhisperModel
except ImportError as err:
    sys.stderr.write("Le package 'faster-whisper' est requis : pip install faster-whisper\n")
    raise err


# ---------------------------------------------------------------------------
# Configuration du logging
# ---------------------------------------------------------------------------
DEFAULT_LOG_FILE = Path(__file__).resolve().parent / "transcriber.log"
DEFAULT_OUTPUT_FILE = Path(__file__).resolve().parent / "live_session.md"

logger = logging.getLogger("live_transcriber")


def setup_logger(log_file: Path, verbose: bool = False):
    """Configure la journalisation simultanée vers la console et un fichier rotatif."""
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except AttributeError:
            pass

    logger.setLevel(logging.DEBUG if verbose else logging.INFO)
    logger.handlers.clear()

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )

    # Console
    c_handler = logging.StreamHandler(sys.stdout)
    c_handler.setFormatter(formatter)
    c_handler.setLevel(logging.DEBUG if verbose else logging.INFO)
    logger.addHandler(c_handler)

    # Fichier rotatif
    try:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        f_handler = RotatingFileHandler(
            str(log_file),
            maxBytes=5 * 1024 * 1024,  # 5 Mo
            backupCount=3,
            encoding="utf-8",
        )
        f_handler.setFormatter(formatter)
        f_handler.setLevel(logging.DEBUG)
        logger.addHandler(f_handler)
    except Exception as e:
        logger.warning("Impossible d'initialiser le fichier de log %s : %s", log_file, e)


# ---------------------------------------------------------------------------
# Chargement du modèle Whisper avec Fail-Fast / Fallback contrôlé
# ---------------------------------------------------------------------------
def load_whisper_model(model_name: str = "medium", device: str = "cuda", compute_type: str = "float16"):
    """Charge le modèle Whisper avec stratégie CUDA nominale et fallbacks explicites."""
    if device == "cuda":
        # 1. Tentative nominale demandée
        try:
            logger.info("Chargement Faster-Whisper '%s' sur device='%s', compute_type='%s'...", model_name, device, compute_type)
            model = WhisperModel(model_name, device="cuda", compute_type=compute_type)
            logger.info("Modèle Whisper '%s' initialisé avec succès sur CUDA (%s).", model_name, compute_type)
            return model, "cuda", compute_type
        except Exception as e:
            logger.warning("Échec du chargement CUDA %s : %s", compute_type, e)

        # 2. Fallback CUDA int8_float16 si float16 échoue
        if compute_type != "int8_float16":
            try:
                logger.info("Tentative fallback CUDA int8_float16...")
                model = WhisperModel(model_name, device="cuda", compute_type="int8_float16")
                logger.info("Modèle Whisper '%s' initialisé avec succès sur CUDA (int8_float16).", model_name)
                return model, "cuda", "int8_float16"
            except Exception as e:
                logger.warning("Échec du chargement CUDA int8_float16 : %s", e)

        # 3. Fallback final CPU int8
        logger.warning("Basculement sur le mode de secours CPU (int8)...")
        model = WhisperModel(model_name, device="cpu", compute_type="int8")
        logger.info("Modèle Whisper '%s' initialisé avec succès sur CPU (int8).", model_name)
        return model, "cpu", "int8"
    else:
        logger.info("Chargement Faster-Whisper '%s' sur CPU...", model_name)
        model = WhisperModel(model_name, device="cpu", compute_type=compute_type or "int8")
        return model, "cpu", compute_type or "int8"


# ---------------------------------------------------------------------------
# Mémoire glissante pour le serveur HTTP
# ---------------------------------------------------------------------------
class TranscriptionMemory:
    """Conserve les segments transcrits récents de manière thread-safe."""
    def __init__(self, max_history_hours: float = 24.0):
        self.lock = threading.Lock()
        self.segments = []  # dict: {timestamp, time_str, text}
        self.max_history_seconds = max_history_hours * 3600.0

    def append(self, text: str, time_str: str, timestamp: float):
        with self.lock:
            self.segments.append({
                "timestamp": timestamp,
                "time": time_str,
                "text": text,
            })
            cutoff = timestamp - self.max_history_seconds
            self.segments = [s for s in self.segments if s["timestamp"] >= cutoff]

    def get_recent(self, minutes: float = 10.0):
        now = time.time()
        cutoff = now - (minutes * 60.0)
        with self.lock:
            matched = [s for s in self.segments if s["timestamp"] >= cutoff]

        full_text = "\n".join(s["text"] for s in matched)
        return {
            "minutes": minutes,
            "count": len(matched),
            "text": full_text,
            "segments": matched,
            "timestamp": datetime.now().isoformat(),
        }

    def total_count(self):
        with self.lock:
            return len(self.segments)


# ---------------------------------------------------------------------------
# Gestionnaire de fichier Markdown local (Append-only avec fsync)
# ---------------------------------------------------------------------------
def resolve_output_path(output_arg: Optional[str] = None) -> Path:
    """Résout le chemin cible de transcription."""
    if output_arg:
        target = Path(output_arg).resolve()
    else:
        target = DEFAULT_OUTPUT_FILE

    target.parent.mkdir(parents=True, exist_ok=True)
    return target


class MarkdownSessionWriter:
    """Assure l'écriture append-only continue et sécurisée dans live_session.md."""
    def __init__(self, target_file: Path):
        self.target_file = Path(target_file).resolve()
        self.target_file.parent.mkdir(parents=True, exist_ok=True)
        self.lock = threading.Lock()

    def ensure_file(self) -> Path:
        if not self.target_file.exists():
            today_str = datetime.now().strftime("%Y-%m-%d")
            header = (
                f"---\n"
                f"type: voicenote\n"
                f"title: \"Live Session {today_str}\"\n"
                f"date: \"{today_str}\"\n"
                f"tags:\n"
                f"  - live-session\n"
                f"---\n\n"
                f"# 🎙️ Live Session {today_str}\n\n"
            )
            self.target_file.write_text(header, encoding="utf-8")
            logger.info("Fichier de session initialisé : %s", self.target_file)
        return self.target_file

    def ensure_file_for_today(self) -> Path:
        """Alias pour rétro-compatibilité."""
        return self.ensure_file()

    def write_segment(self, time_str: str, text: str):
        with self.lock:
            file_path = self.ensure_file()
            line = f"**[{time_str}]** {text}\n\n"
            with open(file_path, "a", encoding="utf-8") as f:
                f.write(line)
                f.flush()
                os.fsync(f.fileno())


# ---------------------------------------------------------------------------
# Serveur HTTP ultra-léger
# ---------------------------------------------------------------------------
def start_http_server(memory: TranscriptionMemory, audio_status_getter, port: int = 3055, host: str = "0.0.0.0"):
    """Lance le serveur HTTP intégré dans un thread démon d'arrière-plan."""
    class TranscriberHTTPHandler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            parsed = urlparse(self.path)
            if parsed.path == "/recent":
                params = parse_qs(parsed.query)
                minutes = 10.0
                if "minutes" in params:
                    try:
                        minutes = float(params["minutes"][0])
                    except ValueError:
                        minutes = 10.0

                data = memory.get_recent(minutes)
                payload = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")

                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(payload)))
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(payload)

            elif parsed.path in ("/status", "/health"):
                status_info = audio_status_getter()
                data = {
                    "status": "running",
                    "uptime_segments": memory.total_count(),
                    "audio": status_info,
                    "timestamp": datetime.now().isoformat(),
                }
                payload = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(payload)))
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(payload)

            else:
                self.send_response(404)
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.end_headers()
                self.wfile.write(b"Endpoint inconnu. Utilisez /recent?minutes=10 ou /status")

        def log_message(self, format, *args):
            pass

    server = http.server.ThreadingHTTPServer((host, port), TranscriberHTTPHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True, name="HTTPServerThread")
    thread.start()
    logger.info("Serveur HTTP API actif sur http://localhost:%d/recent?minutes=10", port)
    return server


# ---------------------------------------------------------------------------
# Gestionnaire de capture audio mixée (Microphone + Discord/Loopback WASAPI)
# ---------------------------------------------------------------------------
class DualAudioCapture:
    """
    Gestionnaire de capture audio mixée :
    - Flux 1 (Maître) : Microphone physique (HyperX QuadCast).
    - Flux 2 (Esclave) : Sortie audio PC / Discord (WASAPI Loopback).
    
    Architecture Fail-Safe & Zéro Jitter :
    - Utilise des callbacks haute priorité via PyAudioWPatch.
    - Le flux Loopback alimente un tampon glissant court non-bloquant.
    - Le flux Microphone consomme ce tampon sans jamais attendre ni bloquer.
    - Si le loopback est silencieux, en erreur ou déconnecté, le micro continue
      d'enregistrer et de transcrire de façon 100% inaltérée.
    """
    def __init__(self, enable_loopback: bool = True, input_device=None, loopback_device=None):
        self.enable_loopback = enable_loopback
        self.input_device = input_device
        self.loopback_device = loopback_device
        self.audio_q = queue.Queue()
        self.stop_event = threading.Event()
        
        self.p = None
        self.s_mic = None
        self.s_loop = None
        self.sd_stream = None

        self.loop_buffer = collections.deque(maxlen=10)
        self.loop_lock = threading.Lock()

        # Métriques de monitoring en direct
        self.mic_chunks_count = 0
        self.loop_chunks_count = 0
        self.last_mic_rms = 0.0
        self.last_loop_rms = 0.0
        self.last_mixed_rms = 0.0
        self.mic_device_name = "Inconnu"
        self.loop_device_name = "Désactivé"

    def start(self):
        use_pyaudio = False
        if HAS_PYAUDIOWPATCH and sys.platform == "win32":
            try:
                self._start_pyaudio()
                use_pyaudio = True
            except Exception as e:
                logger.warning("Échec initialisation PyAudioWPatch : %s. Bascule de secours sur sounddevice.", e)
                self.stop()

        if not use_pyaudio:
            logger.info("Démarrage capture microphone de secours via sounddevice (16 kHz Mono)...")
            self._start_sounddevice_stream()

    def _start_pyaudio(self):
        self.p = pyaudio.PyAudio()
        wasapi_info = self.p.get_host_api_info_by_type(pyaudio.paWASAPI)

        # 1. Résolution du Microphone
        if self.input_device is not None:
            if str(self.input_device).isdigit():
                mic_info = self.p.get_device_info_by_index(int(self.input_device))
            else:
                mic_info = next((self.p.get_device_info_by_index(i) for i in range(self.p.get_device_count())
                                 if str(self.input_device).lower() in self.p.get_device_info_by_index(i)["name"].lower()
                                 and self.p.get_device_info_by_index(i)["maxInputChannels"] > 0), None)
                if not mic_info:
                    mic_info = self.p.get_device_info_by_index(wasapi_info["defaultInputDevice"])
        else:
            mic_info = self.p.get_device_info_by_index(wasapi_info["defaultInputDevice"])

        self.mic_device_name = mic_info["name"]
        mic_ch = int(mic_info["maxInputChannels"])
        mic_rate = int(mic_info["defaultSampleRate"])
        mic_frames = int(mic_rate * 0.1)  # 100 ms

        logger.info("Microphone WASAPI : %s (idx %d, %d ch, %d Hz)", self.mic_device_name, mic_info["index"], mic_ch, mic_rate)

        # 2. Résolution du Loopback (Sortie son PC / Discord)
        loop_info = None
        if self.enable_loopback:
            try:
                if self.loopback_device is not None:
                    if str(self.loopback_device).isdigit():
                        loop_info = self.p.get_device_info_by_index(int(self.loopback_device))
                    else:
                        loop_info = next((d for d in self.p.get_loopback_device_info_generator()
                                         if str(self.loopback_device).lower() in d["name"].lower()), None)
                else:
                    def_out = self.p.get_device_info_by_index(wasapi_info["defaultOutputDevice"])
                    loopbacks = [d for d in self.p.get_loopback_device_info_generator() if def_out["name"] in d["name"]]
                    if not loopbacks:
                        loopbacks = list(self.p.get_loopback_device_info_generator())
                    if loopbacks:
                        loop_info = loopbacks[0]

                if loop_info:
                    self.loop_device_name = loop_info["name"]
                    loop_ch = int(loop_info["maxInputChannels"])
                    loop_rate = int(loop_info["defaultSampleRate"])
                    loop_frames = int(loop_rate * 0.1)  # 100 ms
                    logger.info("Sortie Discord/PC WASAPI Loopback : %s (idx %d, %d ch, %d Hz)", self.loop_device_name, loop_info["index"], loop_ch, loop_rate)
            except Exception as e:
                logger.warning("Échec détection Loopback : %s (continuation micro seul)", e)
                loop_info = None

        # 3. Callbacks haute priorité
        def loop_callback(in_data, frame_count, time_info, status):
            try:
                arr = np.frombuffer(in_data, dtype=np.float32)
                if loop_ch > 1:
                    arr = arr.reshape(-1, loop_ch).mean(axis=1)

                # Rééchantillonnage vers 16 kHz
                if loop_rate == 48000:
                    arr_16k = arr[: len(arr) - len(arr) % 3].reshape(-1, 3).mean(axis=1)
                elif loop_rate == 16000:
                    arr_16k = arr
                else:
                    step = loop_rate / 16000.0
                    idx = (np.arange(int(len(arr) / step)) * step).astype(int)
                    arr_16k = arr[idx]

                rms = float(np.sqrt(np.mean(arr_16k**2)))
                self.last_loop_rms = rms

                with self.loop_lock:
                    if len(self.loop_buffer) >= 3:
                        self.loop_buffer.popleft()  # Élimination immédiate du surplus pour zéro latence
                    self.loop_buffer.append(arr_16k)

                self.loop_chunks_count += 1
            except Exception as exc:
                logger.error("Erreur loop_callback: %s", exc)
            return (None, pyaudio.paContinue)

        def mic_callback(in_data, frame_count, time_info, status):
            try:
                arr = np.frombuffer(in_data, dtype=np.float32)
                if mic_ch > 1:
                    arr = arr.reshape(-1, mic_ch).mean(axis=1)

                # Rééchantillonnage vers 16 kHz
                if mic_rate == 48000:
                    mic_16k = arr[: len(arr) - len(arr) % 3].reshape(-1, 3).mean(axis=1)
                elif mic_rate == 16000:
                    mic_16k = arr
                else:
                    step = mic_rate / 16000.0
                    idx = (np.arange(int(len(arr) / step)) * step).astype(int)
                    mic_16k = arr[idx]

                rms_m = float(np.sqrt(np.mean(mic_16k**2)))
                self.last_mic_rms = rms_m

                # Consommation non-bloquante du chunk loopback
                loop_chunk = None
                with self.loop_lock:
                    if len(self.loop_buffer) > 0:
                        loop_chunk = self.loop_buffer.popleft()

                if loop_chunk is not None:
                    n = min(len(mic_16k), len(loop_chunk))
                    mixed = np.clip(mic_16k[:n] + loop_chunk[:n], -1.0, 1.0).astype(np.float32)
                else:
                    mixed = mic_16k

                self.last_mixed_rms = float(np.sqrt(np.mean(mixed**2)))
                self.audio_q.put(mixed)
                self.mic_chunks_count += 1
            except Exception as exc:
                logger.error("Erreur mic_callback: %s", exc)
            return (None, pyaudio.paContinue)

        # 4. Ouverture du stream Loopback (tolérance de panne intégrale)
        if loop_info:
            try:
                self.s_loop = self.p.open(
                    format=pyaudio.paFloat32,
                    channels=loop_ch,
                    rate=loop_rate,
                    input=True,
                    input_device_index=loop_info["index"],
                    frames_per_buffer=loop_frames,
                    stream_callback=loop_callback,
                )
                self.s_loop.start_stream()
                logger.info("Flux WASAPI Loopback initialisé et actif.")
            except Exception as e:
                logger.warning("Échec d'ouverture du flux Loopback : %s. Le micro fonctionnera seul.", e)
                self.s_loop = None

        # 5. Ouverture du stream Microphone
        self.s_mic = self.p.open(
            format=pyaudio.paFloat32,
            channels=mic_ch,
            rate=mic_rate,
            input=True,
            input_device_index=mic_info["index"],
            frames_per_buffer=mic_frames,
            stream_callback=mic_callback,
        )
        self.s_mic.start_stream()
        logger.info("Flux Microphone initialisé et actif.")

    def _start_sounddevice_stream(self):
        block_size = 1600  # 100 ms à 16 kHz
        self.mic_device_name = f"sounddevice (idx {self.input_device or 'default'})"
        self.loop_device_name = "Désactivé (mode sounddevice)"

        def audio_callback(indata, frames, time_info, status):
            if status:
                logger.warning("Statut audio sounddevice : %s", status)
            flat = indata.copy().flatten()
            self.last_mic_rms = float(np.sqrt(np.mean(flat**2)))
            self.last_mixed_rms = self.last_mic_rms
            self.mic_chunks_count += 1
            self.audio_q.put(flat)

        self.sd_stream = sd.InputStream(
            samplerate=16000,
            channels=1,
            dtype="float32",
            blocksize=block_size,
            device=int(self.input_device) if self.input_device and str(self.input_device).isdigit() else self.input_device,
            callback=audio_callback,
        )
        self.sd_stream.start()
        logger.info("Stream sounddevice démarré.")

    def get_chunk(self, timeout=0.5):
        return self.audio_q.get(timeout=timeout)

    def get_status(self):
        return {
            "microphone": self.mic_device_name,
            "loopback": self.loop_device_name,
            "mic_rms": round(self.last_mic_rms, 5),
            "loop_rms": round(self.last_loop_rms, 5),
            "mixed_rms": round(self.last_mixed_rms, 5),
            "mic_chunks": self.mic_chunks_count,
            "loop_chunks": self.loop_chunks_count,
            "queue_size": self.audio_q.qsize(),
        }

    def stop(self):
        self.stop_event.set()
        if self.sd_stream:
            try:
                self.sd_stream.stop()
                self.sd_stream.close()
            except Exception:
                pass
            self.sd_stream = None

        if self.s_mic:
            try:
                self.s_mic.stop_stream()
                self.s_mic.close()
            except Exception:
                pass
            self.s_mic = None

        if self.s_loop:
            try:
                self.s_loop.stop_stream()
                self.s_loop.close()
            except Exception:
                pass
            self.s_loop = None

        if self.p:
            try:
                self.p.terminate()
            except Exception:
                pass
            self.p = None


# ---------------------------------------------------------------------------
# Filtrage des hallucinations Whisper
# ---------------------------------------------------------------------------
HALLUCINATION_PATTERNS = [
    "merci d'avoir regardé",
    "merci d'avoir visionné",
    "amara.org",
    "sous-titrage",
    "sous-titres réalisés",
    "sous-titres fait",
    "abonnez-vous",
    "n'oubliez pas de vous abonner",
    "à bientôt pour une nouvelle vidéo",
    "watching!",
    "thanks for watching",
]


def is_hallucination(text: str) -> bool:
    """Détecte si un texte transcrit correspond aux artefacts classiques de fin de vidéo YouTube."""
    clean = text.strip().lower()
    if not clean or clean in (".", "...", "!", "?"):
        return True

    for pat in HALLUCINATION_PATTERNS:
        if pat in clean:
            # Si le segment ne contient pratiquement que la phrase d'hallucination, on le rejette
            remainder = clean.replace(pat, "").strip(" .,!?:;-\"'")
            if len(remainder) < 15:
                return True
    return False


# ---------------------------------------------------------------------------
# Boucle principale de capture et de transcription
# ---------------------------------------------------------------------------
def run_transcription_loop(
    model: WhisperModel,
    writer: MarkdownSessionWriter,
    memory: TranscriptionMemory,
    capture: DualAudioCapture,
    sample_rate: int = 16000,
    block_duration: float = 0.1,  # 100 ms par bloc audio
    energy_threshold: float = 0.010,
    silence_duration: float = 1.0,
    max_speech_duration: float = 20.0,
    language: str = "fr",
    max_test_duration: Optional[float] = None,
):
    """Capture le flux audio mixé (Microphone + Discord) et orchestre l'inférence Whisper."""
    pre_buffer_len = int(0.5 / block_duration)  # 500 ms de pré-buffer
    pre_buffer = collections.deque(maxlen=pre_buffer_len)

    speech_chunks = []
    is_speaking = False
    silence_blocks = 0
    silence_blocks_threshold = int(silence_duration / block_duration)
    max_speech_blocks = int(max_speech_duration / block_duration)

    loop_start_time = time.time()
    last_monitor_log = time.time()

    def flush_current_speech():
        nonlocal is_speaking, speech_chunks, silence_blocks
        if speech_chunks and len(speech_chunks) >= int(0.5 / block_duration):
            audio_data = np.concatenate(speech_chunks)
            duration = len(audio_data) / sample_rate
            if duration >= 0.5:
                try:
                    segments, info = model.transcribe(
                        audio_data,
                        language=language,
                        vad_filter=True,
                        vad_parameters=dict(min_silence_duration_ms=400, speech_pad_ms=200),
                        beam_size=5,
                    )
                    segment_texts = []
                    for s in segments:
                        t = s.text.strip()
                        if t and not is_hallucination(t):
                            segment_texts.append(t)

                    if segment_texts:
                        full_text = " ".join(segment_texts)
                        now = time.time()
                        datetime_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        time_display = datetime.now().strftime("%H:%M:%S")

                        logger.info("[TRANSCRIBE] %s", full_text)

                        writer.write_segment(datetime_str, full_text)
                        memory.append(full_text, datetime_str, now)
                except Exception as e:
                    logger.error("Erreur lors de la transcription Whisper : %s", e)
        is_speaking = False
        speech_chunks = []
        silence_blocks = 0
        pre_buffer.clear()

    logger.info("Transcription active (Seuil RMS: %.3f, Silence: %.1fs). Prêt !", energy_threshold, silence_duration)

    try:
        while True:
            if max_test_duration and (time.time() - loop_start_time) >= max_test_duration:
                logger.info("Durée de test atteinte (%.1fs). Vidage des segments...", max_test_duration)
                flush_current_speech()
                break

            try:
                chunk = capture.get_chunk(timeout=0.2)
            except queue.Empty:
                continue

            rms = np.sqrt(np.mean(chunk**2))

            # Logging périodique d'état audio (toutes les 10s)
            if time.time() - last_monitor_log >= 10.0:
                last_monitor_log = time.time()
                logger.debug(
                    "[Audio Monitor] Mic RMS: %.5f | Loop RMS: %.5f | Mixed RMS: %.5f | Speaking: %s",
                    capture.last_mic_rms,
                    capture.last_loop_rms,
                    capture.last_mixed_rms,
                    is_speaking,
                )

            if rms > energy_threshold:
                if not is_speaking:
                    is_speaking = True
                    speech_chunks = list(pre_buffer)
                    silence_blocks = 0
                speech_chunks.append(chunk)
                silence_blocks = 0
            else:
                if is_speaking:
                    speech_chunks.append(chunk)
                    silence_blocks += 1

                    # Détection fin de parole ou durée maximale atteinte
                    if silence_blocks >= silence_blocks_threshold or len(speech_chunks) >= max_speech_blocks:
                        flush_current_speech()
                else:
                    pre_buffer.append(chunk)
    finally:
        flush_current_speech()
        capture.stop()


# ---------------------------------------------------------------------------
# Point d'entrée CLI
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Live Transcriber GPU Faster-Whisper (Micro + Discord)")
    parser.add_argument("--model", default="medium", help="Taille du modèle Faster-Whisper (tiny, base, small, medium, large-v3)")
    parser.add_argument("--device", default="cuda", choices=["cuda", "cpu"], help="Périphérique d'inférence")
    parser.add_argument("--compute-type", default="float16", help="Type de calcul (float16, int8_float16, int8)")
    parser.add_argument("--language", default="fr", help="Code langue (fr, en, ou None pour auto)")
    parser.add_argument("--port", type=int, default=3055, help="Port du serveur HTTP de contexte")
    parser.add_argument("--threshold", type=float, default=0.010, help="Seuil RMS de détection de voix")
    parser.add_argument("--silence", type=float, default=1.0, help="Durée de silence (s) pour valider une phrase")
    parser.add_argument(
        "--output",
        "-o",
        default=None,
        help="Chemin du fichier Markdown de transcription (défaut : live_session.md dans le dossier du script)",
    )
    parser.add_argument(
        "--log-file",
        default=None,
        help="Chemin du fichier de journalisation (défaut : transcriber.log dans le dossier du script)",
    )
    parser.add_argument("--input-device", default=None, help="Nom ou index du microphone d'entrée")
    parser.add_argument("--loopback-device", default=None, help="Nom ou index du périphérique Loopback Discord/PC")
    parser.add_argument("--no-loopback", action="store_true", help="Désactiver le mixage Loopback (Discord/PC)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Activer les logs détaillés DEBUG")
    parser.add_argument("--test", action="store_true", help="Exécuter un test rapide de transcription puis quitter")
    parser.add_argument("--test-duration", type=float, default=12.0, help="Durée du test en secondes (avec --test)")

    args = parser.parse_args()

    # Initialisation des logs
    log_file_path = Path(args.log_file).resolve() if args.log_file else DEFAULT_LOG_FILE
    setup_logger(log_file=log_file_path, verbose=args.verbose)

    logger.info("=== Démarrage Live Transcriber ===")
    logger.info("Arguments : %s", sys.argv[1:])

    # Initialisation du modèle
    lang = None if args.language.lower() in ("none", "auto") else args.language
    model, actual_device, actual_compute = load_whisper_model(
        model_name=args.model,
        device=args.device,
        compute_type=args.compute_type,
    )

    target_output = resolve_output_path(args.output)
    memory = TranscriptionMemory()
    writer = MarkdownSessionWriter(target_file=target_output)
    session_file = writer.ensure_file()
    logger.info("Fichier de session local prêt : %s", session_file)

    capture = DualAudioCapture(
        enable_loopback=not args.no_loopback,
        input_device=args.input_device,
        loopback_device=args.loopback_device,
    )
    capture.start()

    start_http_server(memory=memory, audio_status_getter=capture.get_status, port=args.port)

    test_max_dur = args.test_duration if args.test else None

    try:
        run_transcription_loop(
            model=model,
            writer=writer,
            memory=memory,
            capture=capture,
            energy_threshold=args.threshold,
            silence_duration=args.silence,
            language=lang,
            max_test_duration=test_max_dur,
        )
        if args.test:
            logger.info("Test de transcription complété avec succès.")
    except KeyboardInterrupt:
        logger.info("Interruption demandée par l'utilisateur. Arrêt propre du transcripteur.")
    except Exception as e:
        logger.exception("Erreur fatale du transcripteur : %s", e)
        sys.exit(1)
    finally:
        capture.stop()


if __name__ == "__main__":
    main()
