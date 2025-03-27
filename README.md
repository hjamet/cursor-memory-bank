# Cursor Memory Bank 🧠

## Note to English Speakers 🌍

I apologize, but this repository is primarily in French as it's my personal project that I use daily. I'm making it public in case it might help someone, but I haven't had the time yet to translate it to English or make it more general-purpose. I hope you can still find it useful! 😊

## Installation 🚀

### Method 1: Using git clone (Recommended)

You can install Cursor Memory Bank by cloning the repository:

```bash
git clone https://github.com/hjamet/cursor-memory-bank.git
cd cursor-memory-bank
bash install.sh [options]
```

Available options:
- `--dir <path>` : Install to a specific directory (default: current directory)
- `--no-backup` : Skip backing up existing rules
- `--use-curl` : Force using curl instead of git clone

Examples:
```bash
# Install to current directory
bash install.sh

# Install to a specific directory
bash install.sh --dir /path/to/install

# Skip backup of existing rules
bash install.sh --no-backup

# Force using curl instead of git clone
bash install.sh --use-curl
```

The installation script will:
- Clone the rules to your `.cursor/rules` directory
- Always preserve any existing custom rules
- Create a backup of existing rules (unless --no-backup is used)
- Update only the core rules that need updating
- Preserve any unrelated files that might be in the .cursor directory
- Work even if the .cursor directory already exists

### Method 2: Using curl

You can install using this one-liner:

```bash
curl -fsSL https://raw.githubusercontent.com/hjamet/cursor-memory-bank/main/install.sh | bash -s -- --use-curl
```

For better security, you can also:
1. Download the script first:
```bash
curl -fsSL https://raw.githubusercontent.com/hjamet/cursor-memory-bank/main/install.sh -o install.sh
```

2. Review it:
```bash
less install.sh
```

3. Then run it with any desired options:
```bash
bash install.sh --use-curl [other options]
```

Note: The `--use-curl` option forces the installation to use curl instead of git clone, which can be useful in environments where git is not available or when you prefer not to use git.

## What is Cursor Memory Bank? 🤔

Cursor Memory Bank is a system that helps maintain context between coding sessions by storing and organizing information in a coherent file structure. It's designed to work with Cursor, enhancing its capabilities with structured rules and workflows.

### Features
- 📁 Organized file structure for storing context
- 🔄 Automatic backup of custom rules
- 🛠️ Flexible installation options
- 🔒 Safe updates with rule preservation
- 📝 Structured workflows and rules

## Contributing 🤝

While this is primarily a personal project, contributions are welcome! Just note that most of the documentation and rules are in French. If you'd like to help translate the project to English or improve its general-purpose usage, that would be especially appreciated!

## License 📄

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments 🙏

Thank you for your understanding regarding the French documentation. This project started as a personal tool, and while I'd love to make it more accessible to everyone, I'm sharing it as-is for now, hoping it might still be helpful to some! 