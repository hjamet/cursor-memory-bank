import { Plugin, Notice, TFile } from 'obsidian';
import { jsPDF } from 'jspdf';
import { PDFDocument } from 'pdf-lib';
import * as fs from 'fs/promises';
import * as os from 'os';
import * as path from 'path';
import { exec } from 'child_process';

interface CanvasNode {
  id: string;
  type: 'text' | 'file' | 'link' | 'group';
  x: number;
  y: number;
  width: number;
  height: number;
  color?: string;
  label?: string; // for group
  text?: string;  // for text node
  file?: string;  // for file node
  subpath?: string; // for file node subpath
  url?: string;   // for link node
}

interface CanvasEdge {
  id: string;
  fromNode: string;
  fromSide?: string;
  toNode: string;
  toSide?: string;
}

interface CanvasData {
  nodes: CanvasNode[];
  edges: CanvasEdge[];
}

export default class CanvasExportPlugin extends Plugin {
  async onload() {
    console.log('Loading Canvas Export to PDF & Clipboard plugin...');

    // Add ribbon icon
    this.addRibbonIcon('pdf-file', 'Export Active Canvas to PDF & Clipboard', async () => {
      await this.exportActiveCanvas();
    });

    // Add command palette item
    this.addCommand({
      id: 'export-active-canvas-pdf-clipboard',
      name: 'Export Active Canvas to PDF & Clipboard',
      callback: async () => {
        await this.exportActiveCanvas();
      },
    });
  }

  async exportActiveCanvas() {
    const activeFile = this.app.workspace.getActiveFile();
    
    if (!activeFile || activeFile.extension !== 'canvas') {
      new Notice("⚠️ Veuillez ouvrir un fichier Canvas (.canvas) pour l'exporter.");
      return;
    }

    new Notice("⏳ Analyse du Canvas en cours...");

    try {
      // 1. Read and parse Canvas file
      const canvasContent = await this.app.vault.read(activeFile);
      const data: CanvasData = JSON.parse(canvasContent);

      if (!data.nodes || data.nodes.length === 0) {
        new Notice("ℹ️ Ce Canvas est vide (aucun nœud).");
        return;
      }

      const canvasName = activeFile.basename;
      
      // 2. Parse connections and topology
      const nodeTitles = new Map<string, string>();
      const incoming = new Map<string, string[]>();
      const outgoing = new Map<string, string[]>();

      data.nodes.forEach(n => {
        let title = '';
        if (n.type === 'text') {
          title = n.text ? n.text.split('\n')[0].substring(0, 40) : `Texte (${n.id.substring(0, 6)})`;
          if (title.startsWith('#')) title = title.replace(/^#+\s*/, '');
        } else if (n.type === 'file') {
          title = n.file ? path.basename(n.file) : 'Fichier';
        } else if (n.type === 'link') {
          title = n.url || 'Lien';
        } else if (n.type === 'group') {
          title = n.label || 'Groupe';
        }
        nodeTitles.set(n.id, title);
      });

      if (data.edges) {
        data.edges.forEach(edge => {
          const fromTitle = nodeTitles.get(edge.fromNode) || 'Nœud inconnu';
          const toTitle = nodeTitles.get(edge.toNode) || 'Nœud inconnu';

          if (!outgoing.has(edge.fromNode)) outgoing.set(edge.fromNode, []);
          outgoing.get(edge.fromNode)?.push(toTitle);

          if (!incoming.has(edge.toNode)) incoming.set(edge.toNode, []);
          incoming.get(edge.toNode)?.push(fromTitle);
        });
      }

      // 3. Geometry grouping algorithm
      const groups = data.nodes.filter(n => n.type === 'group');
      const otherNodes = data.nodes.filter(n => n.type !== 'group');

      const isInside = (n: CanvasNode, g: CanvasNode) => {
        return (
          n.id !== g.id &&
          n.x >= g.x &&
          n.y >= g.y &&
          (n.x + n.width) <= (g.x + g.width) &&
          (n.y + n.height) <= (g.y + g.height)
        );
      };

      const groupChildren = new Map<string, CanvasNode[]>();
      groups.forEach(g => groupChildren.set(g.id, []));

      const topLevelNodes: CanvasNode[] = [];

      otherNodes.forEach(node => {
        const containingGroups = groups.filter(g => isInside(node, g));
        if (containingGroups.length > 0) {
          // Sort containing groups by area ascending to find the smallest (innermost) parent group
          containingGroups.sort((a, b) => (a.width * a.height) - (b.width * b.height));
          const parentGroup = containingGroups[0];
          groupChildren.get(parentGroup.id)?.push(node);
        } else {
          topLevelNodes.push(node);
        }
      });

      // Sort functions (by Y primary, X secondary)
      const sortByPosition = (a: CanvasNode, b: CanvasNode) => {
        if (Math.abs(a.y - b.y) > 10) {
          return a.y - b.y;
        }
        return a.x - b.x;
      };

      topLevelNodes.sort(sortByPosition);
      groups.sort(sortByPosition);
      groups.forEach(g => {
        groupChildren.get(g.id)?.sort(sortByPosition);
      });

      // 4. Initialize jsPDF
      const doc = new jsPDF({
        orientation: 'p',
        unit: 'mm',
        format: 'a4',
      });

      const pageWidth = 210;
      const pageHeight = 297;
      const margin = 15;
      const contentWidth = pageWidth - 2 * margin; // 180mm
      let currentY = margin;

      // Color mapping
      const getColorHex = (colorNum?: string) => {
        switch (colorNum) {
          case '1': return '#FF6B6B'; // Red
          case '2': return '#FCA311'; // Orange
          case '3': return '#8AC926'; // Green
          case '4': return '#1982C4'; // Blue
          case '5': return '#6A4C93'; // Purple
          case '6': return '#FF595E'; // Pink
          default: return '#7F8C8D';  // Gray
        }
      };

      // Safe clean text function to remove emojis or non-supported jsPDF Helvetica characters to prevent encoding crashes
      const cleanText = (txt: string): string => {
        if (!txt) return '';
        // Map common accents, remove unmappable emojis/symbols
        return txt
          .normalize('NFD')
          .replace(/[\u0300-\u036f]/g, "") // remove accents for maximum safety in basic Helvetica
          .replace(/[^\x00-\x7F]/g, "?"); // replace non-ascii with ?
      };

      // --- PAGE 1: COVER PAGE ---
      doc.setFillColor(248, 249, 250); // Light gray background stripe
      doc.rect(0, 0, 50, pageHeight, 'F');

      doc.setFont('Helvetica', 'bold');
      doc.setFontSize(26);
      doc.setTextColor(44, 62, 80);
      doc.text(cleanText(canvasName), 60, 60);

      doc.setFont('Helvetica', 'normal');
      doc.setFontSize(12);
      doc.setTextColor(127, 140, 141);
      doc.text("RAPPORT D'EXPORT CANVAS OBSIDIAN", 60, 72);

      // Metadonnées
      doc.setFontSize(10);
      doc.setTextColor(52, 73, 94);
      let metaY = 120;
      doc.text(`Fichier source : ${cleanText(activeFile.name)}`, 60, metaY);
      doc.text(`Date de génération : ${new Date().toLocaleString()}`, 60, metaY + 8);
      doc.text(`Nombre total de nœuds : ${data.nodes.length}`, 60, metaY + 16);
      doc.text(`Nombre total d'arêtes : ${data.edges?.length || 0}`, 60, metaY + 24);

      // Separation line
      doc.setDrawColor(44, 62, 80);
      doc.setLineWidth(1);
      doc.line(60, 160, 180, 160);

      doc.setFont('Helvetica', 'italic');
      doc.setFontSize(9);
      doc.setTextColor(127, 140, 141);
      doc.text("Généré de manière autonome par Antigravity - AI Assistant", 60, 170);

      // --- PAGE 2: TOPOLOGY & RELATIONSHIPS ---
      doc.addPage();
      currentY = margin;

      doc.setFont('Helvetica', 'bold');
      doc.setFontSize(16);
      doc.setTextColor(44, 62, 80);
      doc.text("Structure et Relations du Graphe", margin, currentY + 5);
      currentY += 15;

      doc.setFont('Helvetica', 'normal');
      doc.setFontSize(10);
      doc.setTextColor(52, 73, 94);
      doc.text("Ce document contient les connexions géométriques et sémantiques entre les nœuds du Canvas.", margin, currentY);
      currentY += 10;

      // Draw connection table / text representation of connections
      doc.setFont('Helvetica', 'bold');
      doc.setFontSize(11);
      doc.text("Index des Groupes et Éléments", margin, currentY);
      currentY += 8;

      doc.setFont('Helvetica', 'normal');
      doc.setFontSize(9);
      
      // List groups and their sizes
      doc.text(`• Éléments de premier niveau (orphelins) : ${topLevelNodes.length}`, margin + 5, currentY);
      currentY += 6;
      groups.forEach(g => {
        const count = groupChildren.get(g.id)?.length || 0;
        doc.text(`• Groupe [${cleanText(g.label || 'Sans nom')}] : ${count} éléments`, margin + 5, currentY);
        currentY += 6;
      });

      currentY += 5;
      doc.setFont('Helvetica', 'bold');
      doc.setFontSize(11);
      doc.text("Relations Directes (Arêtes)", margin, currentY);
      currentY += 8;

      doc.setFont('Helvetica', 'normal');
      doc.setFontSize(8);
      if (data.edges && data.edges.length > 0) {
        for (let i = 0; i < Math.min(data.edges.length, 25); i++) {
          const edge = data.edges[i];
          const from = cleanText(nodeTitles.get(edge.fromNode) || 'Inconnu');
          const to = cleanText(nodeTitles.get(edge.toNode) || 'Inconnu');
          doc.text(`  [${from}] ──► [${to}]`, margin + 5, currentY);
          currentY += 5;
          if (currentY > pageHeight - margin) {
            doc.addPage();
            currentY = margin;
          }
        }
        if (data.edges.length > 25) {
          doc.text(`  ... et ${data.edges.length - 25} autres relations.`, margin + 5, currentY);
          currentY += 5;
        }
      } else {
        doc.text("  Aucune liaison explicite définie dans le Canvas.", margin + 5, currentY);
        currentY += 5;
      }

      // --- RENDER NODES PAGES ---
      const renderNode = async (node: CanvasNode, groupLabel?: string) => {
        // Prepare content
        let title = cleanText(nodeTitles.get(node.id) || 'Élément');
        let typeLabel = '';
        let contentString = '';
        let isPdfAttachment = false;

        if (node.type === 'text') {
          typeLabel = 'Note Texte';
          contentString = node.text || '';
        } else if (node.type === 'file') {
          typeLabel = 'Note Fichier';
          if (node.file) {
            const ext = path.extname(node.file).toLowerCase();
            if (ext === '.pdf') {
              typeLabel = 'Annexe PDF';
              contentString = `Fichier PDF : ${node.file}\nLe contenu intégral de ce document PDF est inséré en annexe à la fin de ce rapport.`;
              isPdfAttachment = true;
            } else if (ext === '.md') {
              // Retrieve file content
              const tfile = this.app.metadataCache.getFirstLinkpathDest(node.file, '');
              if (tfile && tfile instanceof TFile) {
                let markdown = await this.app.vault.read(tfile);
                if (node.subpath) {
                  typeLabel = `Note Fichier (Section ${node.subpath})`;
                  markdown = this.extractSubpathContent(markdown, node.subpath);
                }
                contentString = markdown;
              } else {
                contentString = `⚠️ Impossible de charger la note : ${node.file}`;
              }
            } else {
              contentString = `Fichier associé : ${node.file}`;
            }
          }
        } else if (node.type === 'link') {
          typeLabel = 'Lien Web';
          contentString = node.url || 'Aucune URL fournie';
        }

        // Clean content for PDF
        const titleClean = cleanText(title);
        const groupClean = groupLabel ? ` (Groupe: ${cleanText(groupLabel)})` : '';
        const fullHeader = `[${typeLabel}] ${titleClean}${groupClean}`;
        
        // Wrap text
        const wrappedLines = doc.splitTextToSize(contentString, contentWidth - 16) as string[];
        
        // Calculate incoming / outgoing relations text
        const nodeIncoming = incoming.get(node.id) || [];
        const nodeOutgoing = outgoing.get(node.id) || [];
        const relationsLines: string[] = [];
        if (nodeIncoming.length > 0) {
          relationsLines.push(`Connexions entrantes : ${nodeIncoming.map(cleanText).join(', ')}`);
        }
        if (nodeOutgoing.length > 0) {
          relationsLines.push(`Connexions sortantes : ${nodeOutgoing.map(cleanText).join(', ')}`);
        }

        // Estimate required height for the card
        // 10mm header + padding + relations + text lines
        const lineSpacing = 5;
        let estimatedHeight = 15; // border margin
        estimatedHeight += relationsLines.length * 4;
        estimatedHeight += wrappedLines.length * lineSpacing;
        if (estimatedHeight < 25) estimatedHeight = 25; // minimum card height

        // If card doesn't fit on this page, push to next
        if (currentY + estimatedHeight > pageHeight - margin) {
          doc.addPage();
          currentY = margin;
        }

        const startY = currentY;
        currentY += 8; // move down for metadata

        // Draw connections
        doc.setFont('Helvetica', 'normal');
        doc.setFontSize(7);
        doc.setTextColor(120, 120, 120);
        let relY = startY + 9;
        relationsLines.forEach(rel => {
          doc.text(rel, margin + 6, relY);
          relY += 4;
        });

        // Set text starting Y
        currentY = relY + 1;

        // Draw content text
        doc.setFont('Helvetica', 'normal');
        doc.setFontSize(9);
        doc.setTextColor(52, 73, 94);
        wrappedLines.forEach(line => {
          // Extra safety check in case wrapping estimate was slightly off
          if (currentY > pageHeight - margin - 5) {
            // Draw card bottom border on current page
            const partialHeight = currentY - startY + 3;
            doc.setDrawColor(220, 224, 230);
            doc.setFillColor(255, 255, 255, 0); // Transparent fill, just borders
            doc.roundedRect(margin, startY, contentWidth, partialHeight, 2, 2, 'D');
            
            // Left color stripe
            doc.setFillColor(getColorHex(node.color));
            doc.rect(margin, startY + 0.5, 2, partialHeight - 1, 'F');

            doc.addPage();
            currentY = margin + 10;
          }
          doc.text(cleanText(line), margin + 6, currentY);
          currentY += lineSpacing;
        });

        // Compute final card height
        const finalCardHeight = currentY - startY + 3;

        // Draw card border and background
        // First we do a filled rect to mask anything, then stroke
        doc.setGState(new (doc as any).GState({ opacity: 1.0 }));
        doc.setDrawColor(220, 224, 230);
        doc.setFillColor(255, 255, 255, 0); // border only
        doc.roundedRect(margin, startY, contentWidth, finalCardHeight, 2, 2, 'D');

        // Draw pastel left color stripe
        doc.setFillColor(getColorHex(node.color));
        doc.rect(margin, startY + 0.5, 2, finalCardHeight - 1, 'F');

        // Draw header text on top of card
        doc.setFont('Helvetica', 'bold');
        doc.setFontSize(10);
        doc.setTextColor(44, 62, 80);
        doc.text(fullHeader, margin + 6, startY + 6);

        currentY += 8; // spacing after card
      };

      // A. Export top-level nodes first
      for (const node of topLevelNodes) {
        doc.addPage();
        currentY = margin;
        await renderNode(node);
      }

      // B. Export groups and their children
      for (const group of groups) {
        doc.addPage();
        currentY = margin;

        // Header for group
        doc.setFont('Helvetica', 'bold');
        doc.setFontSize(18);
        doc.setTextColor(44, 62, 80);
        const groupHex = getColorHex(group.color);
        
        // Draw a colored group banner
        doc.setFillColor(groupHex);
        doc.rect(margin, currentY, contentWidth, 12, 'F');
        doc.setTextColor(255, 255, 255);
        doc.setFontSize(12);
        doc.text(`GROUPE : ${cleanText(group.label || 'Sans nom')}`, margin + 5, currentY + 8);
        
        currentY += 22;

        const children = groupChildren.get(group.id) || [];
        if (children.length === 0) {
          doc.setFont('Helvetica', 'italic');
          doc.setFontSize(10);
          doc.setTextColor(127, 140, 141);
          doc.text("Ce groupe ne contient aucun élément enfant.", margin, currentY);
          currentY += 10;
        } else {
          for (const child of children) {
            await renderNode(child, group.label);
          }
        }
      }

      // --- HEADERS & FOOTERS POST-PROCESSING ---
      const totalPages = doc.getNumberOfPages();
      for (let i = 2; i <= totalPages; i++) {
        doc.setPage(i);

        // Header
        doc.setFont('Helvetica', 'normal');
        doc.setFontSize(8);
        doc.setTextColor(127, 140, 141);
        doc.text(`Rapport d'export : ${cleanText(canvasName)}`, margin, 9);
        doc.setDrawColor(230, 233, 237);
        doc.setLineWidth(0.2);
        doc.line(margin, 11, pageWidth - margin, 11);

        // Footer
        doc.line(margin, pageHeight - 11, pageWidth - margin, pageHeight - 11);
        doc.text(`Page ${i} sur ${totalPages}`, pageWidth - margin, pageHeight - 7, { align: 'right' });
      }

      // Save main PDF as ArrayBuffer
      const mainPdfBytes = doc.output('arraybuffer');

      // 5. Concatenate Embedded PDFs using pdf-lib
      let finalPdfBytes: Uint8Array = new Uint8Array(mainPdfBytes);
      const pdfNodeFiles = data.nodes.filter(n => n.type === 'file' && n.file?.toLowerCase().endsWith('.pdf'));

      if (pdfNodeFiles.length > 0) {
        new Notice("🔗 Concaténation des annexes PDF en cours...");
        const finalPdf = await PDFDocument.load(mainPdfBytes);

        for (const node of pdfNodeFiles) {
          if (!node.file) continue;
          
          const tfile = this.app.metadataCache.getFirstLinkpathDest(node.file, '');
          if (tfile && tfile instanceof TFile) {
            try {
              const pdfArrayBuffer = await this.app.vault.readBinary(tfile);
              const externalPdf = await PDFDocument.load(pdfArrayBuffer);
              
              const copiedPages = await finalPdf.copyPages(externalPdf, externalPdf.getPageIndices());
              copiedPages.forEach(page => finalPdf.addPage(page));
              console.log(`Successfully merged PDF: ${node.file}`);
            } catch (mergeErr) {
              console.error(`Error merging PDF file ${node.file}:`, mergeErr);
              new Notice(`⚠️ Impossible de concaténer le PDF: ${path.basename(node.file)}`);
            }
          } else {
            new Notice(`⚠️ Fichier PDF introuvable : ${node.file}`);
          }
        }

        finalPdfBytes = await finalPdf.save();
      }

      // 6. Write PDF to Temp Folder
      const tempDir = os.tmpdir();
      const sanitizedCanvasName = canvasName.replace(/[^a-zA-Z0-9_\-]/g, '_');
      const tempPath = path.join(tempDir, `${sanitizedCanvasName}_Export.pdf`);

      await fs.writeFile(tempPath, Buffer.from(finalPdfBytes));
      console.log(`PDF saved temporarily to: ${tempPath}`);

      // 7. Copy to Clipboard using System Commands
      this.copyFileToClipboard(tempPath);

    } catch (err) {
      console.error(err);
      new Notice(`❌ Une erreur est survenue lors de l'export : ${err.message}`);
    }
  }

  extractSubpathContent(markdown: string, subpath: string): string {
    if (!subpath) return markdown;

    const lines = markdown.split(/\r?\n/);

    if (subpath.startsWith('#')) {
      const targetHeading = subpath.replace(/^#+/, '').toLowerCase().trim();
      let startIndex = -1;
      let targetLevel = 0;

      for (let i = 0; i < lines.length; i++) {
        const line = lines[i].trim();
        if (line.startsWith('#')) {
          const match = line.match(/^(#+)\s+(.*)$/);
          if (match) {
            const level = match[1].length;
            const text = match[2].toLowerCase().trim();
            if (text === targetHeading || targetHeading.endsWith(text) || text.endsWith(targetHeading)) {
              startIndex = i;
              targetLevel = level;
              break;
            }
          }
        }
      }

      if (startIndex !== -1) {
        const extractedLines: string[] = [];
        extractedLines.push(lines[startIndex]);

        for (let i = startIndex + 1; i < lines.length; i++) {
          const line = lines[i];
          const trimmed = line.trim();
          if (trimmed.startsWith('#')) {
            const match = trimmed.match(/^(#+)\s+(.*)$/);
            if (match) {
              const level = match[1].length;
              if (level <= targetLevel) {
                break;
              }
            }
          }
          extractedLines.push(line);
        }
        return extractedLines.join('\n');
      }
    }

    return markdown; // fallback
  }

  copyFileToClipboard(tempPath: string) {
    const isWindows = process.platform === 'win32';
    const isMac = process.platform === 'darwin';

    if (isWindows) {
      // Escape single quotes for PowerShell
      const escapedPath = tempPath.replace(/'/g, "''");
      const cmd = `powershell.exe -NoProfile -Command "Get-Item -LiteralPath '${escapedPath}' | Set-Clipboard"`;
      
      exec(cmd, (error, stdout, stderr) => {
        if (error) {
          console.error("PowerShell clipboard error:", error, stderr);
          new Notice(`⚠️ PDF généré dans le dossier Temp, mais erreur de copie presse-papier.`);
        } else {
          new Notice("🎉 PDF exporté et copié dans le presse-papier !");
        }
      });
    } else if (isMac) {
      // AppleScript for macOS
      const cmd = `osascript -e 'set the clipboard to (POSIX file "${tempPath}")'`;
      
      exec(cmd, (error, stdout, stderr) => {
        if (error) {
          console.error("macOS AppleScript clipboard error:", error, stderr);
          new Notice(`⚠️ PDF généré, mais erreur de copie presse-papier.`);
        } else {
          new Notice("🎉 PDF exporté et copié dans le presse-papier !");
        }
      });
    } else {
      new Notice(`ℹ️ PDF généré à l'emplacement : ${tempPath} (Copie presse-papier non supportée sur cet OS).`);
    }
  }
}
