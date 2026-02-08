# Sysmo-USIM-Tool GUI

A graphical user interface for batch programming SysmoUSIM cards.

## Features

✅ **Card Support**
- sysmoISIM-SJA2
- sysmoISIM-SJA5 (with TUAK/5G support)
- sysmoUSIM-SJS1

✅ **Core Features**
- CSV batch programming
- Card detection and authentication
- JSON backup/restore
- Validation with error highlighting
- Progress tracking
- Comprehensive logging

✅ **CSV Format**
- Basic parameters (IMSI, ICCID, Ki, OPc, algorithms)
- Advanced parameters (Milenage R/C, TUAK, SQN)
- Load standard CSV or card-parameters.txt files

## Installation

### Prerequisites

```bash
# Ubuntu/Debian
sudo apt-get install python3 python3-tk python3-pyscard pcscd libpcsclite-dev

# Start PC/SC daemon
sudo systemctl start pcscd
sudo systemctl enable pcscd
```

### Verify Installation

```bash
# Check card reader
pcsc_scan

# Check Python modules
python3 -c "import tkinter; print('✓ tkinter')"
python3 -c "import smartcard; print('✓ pyscard')"
```

## Running the GUI

```bash
cd /opt/sysmo-usim-tool
python3 gui_main.py
```

Or make it executable:

```bash
chmod +x gui_main.py
./gui_main.py
```

## Quick Start

### 1. Prepare CSV File

Create a CSV file with your card configurations. See `test_cards.csv` for an example.

**Minimum required columns:**
```csv
IMSI,ICCID,Ki,OPc,ALGO_2G,ALGO_3G,ALGO_4G5G,MNC_LENGTH
001010000000001,8988211000000000001,00112233445566778899AABBCCDDEEFF,ABCDEF0123456789ABCDEF0123456789,MILENAGE,MILENAGE,MILENAGE,2
```

### 2. Launch GUI

```bash
python3 gui_main.py
```

### 3. Load CSV

- Click **"Load CSV"** button
- Select your CSV file
- Verify data in table (errors highlighted in red)

### 4. Insert Card & Detect

- Insert your card into the reader
- Click **"Detect Card"** (or press F5)
- Verify card type is detected correctly

### 5. Authenticate

- Click **"Authenticate"** button
- Enter your 8-digit ADM1 key
- ⚠️ **WARNING**: Wrong ADM1 will lock your card after 3 attempts!

### 6. Start Batch Programming

- Click **"Start Batch"** button
- Follow prompts to insert each card
- Monitor progress in right panel

## GUI Layout

```
┌─────────────────────────────────────────────────────────────┐
│ File  Card  Batch  Help                                      │
├────────────────────────┬────────────────────────────────────┤
│ Card Status            │ Batch Programming Progress         │
│ ○ sysmoISIM-SJA5       │ Current Card: 2 of 5              │
│ IMSI: 001010000000001  │ Status: Programming...            │
│ [Detect] [Authenticate]│ Progress: ████████░░░░ 45%        │
├────────────────────────┤ Success: 1  Failed: 0  Skip: 0    │
│ Card Configurations    │ [Start] [Pause] [Skip] [Stop]     │
│ [Load] [Save] [Add]    ├────────────────────────────────────┤
│ # IMSI         ICCID   │ Log                                │
│ 1 001010000... 8988... │ [10:15:23] Card detected: SJA5    │
│ 2 001010000... 8988... │ [10:15:25] Authentication OK       │
│ 3 001010000... 8988... │ [10:15:30] Programming card 1...  │
└────────────────────────┴────────────────────────────────────┘
```

## Menu Options

### File Menu
- **Load CSV** - Load card configurations from CSV
- **Save CSV** - Save current configurations
- **Load card-parameters.txt** - Import from Sysmocom format
- **Exit** - Close application

### Card Menu
- **Detect Card** (Ctrl+D / F5) - Detect inserted card
- **Authenticate** - Enter ADM1 key
- **Backup Current Card** - Create JSON backup

### Batch Menu
- **Start Batch Programming** - Begin batch operation
- **IMSI Editor** - Generate sequential IMSIs (coming soon)

### Help Menu
- **About** - Application information

## Keyboard Shortcuts

- `Ctrl+O` - Load CSV
- `Ctrl+S` - Save CSV
- `Ctrl+D` or `F5` - Detect card

## CSV Format Details

### Basic Columns (Required)

| Column | Format | Example | Description |
|--------|--------|---------|-------------|
| IMSI | 15 digits | 001010000000001 | International Mobile Subscriber Identity |
| ICCID | 19-20 digits | 8988211000000000001 | Integrated Circuit Card ID |
| Ki | 32 hex chars | 00112233...EEFF | Authentication key (128-bit) |
| OPc | 32 hex chars | ABCDEF01...6789 | Operator code (for MILENAGE) |
| ALGO_2G | String | MILENAGE | 2G algorithm |
| ALGO_3G | String | MILENAGE | 3G algorithm |
| ALGO_4G5G | String | MILENAGE | 4G/5G algorithm (SJA2/5 only) |
| MNC_LENGTH | 1-2 | 2 | MNC length |

### Advanced Columns (Optional)

- **Milenage R**: MILENAGE_R1 through MILENAGE_R5 (1 byte hex each)
- **Milenage C**: MILENAGE_C1 through MILENAGE_C5 (16 bytes hex each)
- **TUAK** (SJA5 only): TUAK_RES_SIZE, TUAK_MAC_SIZE, TUAK_CKIK_SIZE, TUAK_NUM_KECCAK
- **OP/OPc**: USE_OPC (1=use OPc, 0=use OP)

### Supported Algorithms

- **COMP128v1, COMP128v2, COMP128v3** - GSM algorithms
- **MILENAGE** - 3GPP standard (3G/4G)
- **SHA1-AKA** - Alternative 3G/4G algorithm
- **XOR** - Simple XOR-based algorithm
- **XOR-2G** - 2G-specific XOR (SJA5 only)
- **TUAK** - 5G algorithm (SJA5 only)

## Backup Files

Backups are stored in `./backups/` as JSON files:

```
backups/backup_8988211000000000001_20260206_101525.json
```

Format:
```json
{
  "backup_version": "1.0",
  "timestamp": "2026-02-06T10:15:25",
  "card_type": "SJA5",
  "card_data": {
    "imsi": "001010000000001",
    "iccid": "8988211000000000001",
    "authentication": { ... },
    "milenage_params": { ... }
  }
}
```

## Safety Features

⚠️ **Authentication Protection**
- Shows remaining attempts before authentication
- Warns if attempts < 3
- Requires confirmation for risky operations

✅ **Validation**
- Real-time CSV validation
- Error highlighting in table
- Detailed error messages in log

✅ **Backup**
- Optional automatic backup before programming
- JSON format with full restore capability
- Timestamped filenames

## Troubleshooting

### Card Not Detected

```bash
# Check PC/SC daemon
sudo systemctl status pcscd

# Check card reader
pcsc_scan

# Check permissions
sudo usermod -aG plugdev $USER
```

### Python Module Errors

```bash
# Install missing modules
sudo apt-get install python3-tk python3-pyscard

# Or in venv
pip install pyscard pycryptodome
```

### Authentication Fails

⚠️ **STOP!** Do not retry with wrong ADM1!

- Verify ADM1 key from card carrier or documentation
- Check remaining attempts (shown in dialog)
- Card locks permanently after 3 failed attempts

### CSV Validation Errors

- Check CSV format matches specification
- Verify hex strings (only 0-9, A-F)
- Ensure required fields are present
- See log for detailed error messages

## Development Status

### ✅ Implemented
- Core backend (card management, CSV parsing, validation)
- GUI framework and main window
- Card detection and authentication
- CSV editor with table view
- Progress tracking
- Logging system
- Backup/restore infrastructure

### 🚧 Coming Soon
- Full batch programming orchestration
- IMSI pattern editor dialog
- Restore from backup
- Advanced parameter editing
- Card comparison tool

## File Structure

```
sysmo-usim-tool/
├── gui_main.py              # Main GUI application
├── managers/
│   ├── card_manager.py      # Card operations
│   ├── csv_manager.py       # CSV handling
│   └── backup_manager.py    # Backup/restore
├── widgets/
│   ├── card_status_panel.py # Card status display
│   ├── csv_editor_panel.py  # CSV table editor
│   └── progress_panel.py    # Progress tracking
├── dialogs/
│   └── adm1_dialog.py       # ADM1 input dialog
├── utils/
│   ├── validators.py        # Data validation
│   └── card_detector.py     # Card type detection
├── test_cards.csv           # Example CSV
└── backups/                 # Backup directory
```

## License

This GUI extension follows the original sysmo-usim-tool license (GPL v2).

## Support

For issues or questions:
- Check log output for detailed error messages
- Verify hardware setup with `pcsc_scan`
- Ensure correct ADM1 key from card documentation

## Credits

Built on top of the sysmocom sysmo-usim-tool project.

GUI developed for batch programming workflows.
