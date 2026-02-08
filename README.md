sysmo-usim-tool
===============

Python utility for configuring vendor-specific parameters of sysmocom programmable SIM/USIM/ISIM cards.

**Version 1.0** includes both command-line tools and a graphical user interface (GUI) for batch programming operations.

For more information about the SIM cards, see the [user manual](https://www.sysmocom.de/manuals/sysmousim-manual.pdf)

## Supported Cards

### sysmoISIM-SJA2
Programmable and Java-capable USIM, ISIM and HPSIM card with per-card ADM1 keys.
- https://osmocom.org/projects/cellular-infrastructure/wiki/SysmoISIM-SJA2
- Available from [sysmocom webshop](http://shop.sysmocom.de/products/sysmoISIM-SJA2)

### sysmoISIM-SJA5
Enhanced version with TUAK support for 5G authentication.
- Full 4G/5G compatibility with MILENAGE and TUAK algorithms

### sysmoUSIM-SJS1
Programmable and Java-capable USIM card with per-card ADM1 keys.
- https://osmocom.org/projects/cellular-infrastructure/wiki/SysmoUSIM-SJS1

All cards use separate ADM1 keys and are hacker/developer friendly (writable fields, reduced security for applet installation).

## Features

### GUI Application (New in v1.0)
- **Batch Programming**: Program multiple cards sequentially from CSV file
- **Card Detection**: Auto-detect card type (SJA2/SJA5/SJS1)
- **CSV Editor**: Edit card configurations in table view
- **Backup/Restore**: Create JSON backups before programming
- **Real-time Validation**: Verify card data after programming
- **Progress Tracking**: Monitor batch operations with success/failed/skipped counts
- **Manual Card Editor**: Read/write individual cards with validation
- **IMSI Pattern Generator**: Create sequential IMSI configurations

### Command-Line Tools
- `sysmo-usim-tool.sjs1.py`: Program sysmoUSIM-SJS1 cards
- `sysmo-isim-sja2-tool.py`: Program sysmoISIM-SJA2/SJA5 cards
- Full support for MILENAGE, COMP128, TUAK algorithms

## Prerequisites

### System Requirements
- **Python**: 3.8 or newer (tested with 3.12.3)
- **Operating System**: Linux (Ubuntu/Debian), macOS
- **Smart Card Reader**: PC/SC compatible reader

### System Dependencies

#### Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install python3 python3-pip python3-tk pcscd pcsc-tools
sudo systemctl start pcscd
sudo systemctl enable pcscd
```

#### macOS:
```bash
brew install python3 python-tk@3.12
# PC/SC daemon is built into macOS
```

#### Fedora/RHEL:
```bash
sudo dnf install python3 python3-pip python3-tkinter pcsc-lite pcsc-tools
sudo systemctl start pcscd
sudo systemctl enable pcscd
```

### Python Dependencies

#### pyscard (Smart Card Library)
**Ubuntu/Debian** (recommended - installs both library and Python bindings):
```bash
sudo apt-get install python3-pyscard
```

**Alternative - pip install** (requires PCSC development files):
```bash
# Install PCSC development files first
sudo apt-get install libpcsclite-dev swig

# Then install pyscard
pip3 install pyscard
```

**macOS**:
```bash
pip3 install pyscard
```

#### Verify pyscard installation:
```bash
python3 -c "from smartcard.System import readers; print(readers())"
```
Should list your connected card readers.

## Fresh Installation

### 1. Clone Repository
```bash
git clone https://github.com/SeJohnEff/sysmo-usim-tool.git
cd sysmo-usim-tool
```

### 2. Install System Dependencies
```bash
# Ubuntu/Debian
sudo apt-get install python3-pyscard python3-tk pcscd pcsc-tools
sudo systemctl start pcscd

# Verify card reader is detected
pcsc_scan
```

### 3. Test Installation
```bash
# Verify Python version (3.8+)
python3 --version

# Verify pyscard
python3 -c "from smartcard.System import readers; print(readers())"

# Insert a card and test detection
python3 -c "from utils.card_detector import CardDetector; print(CardDetector.create_card_object())"
```

## Usage

### GUI Application (Recommended for Batch Operations)

Start the GUI:
```bash
python3 gui_main.py
```

#### Typical Workflow:
1. **Load CSV**: File → Load CSV or File → Load card-parameters.txt
2. **Insert Card**: Insert first card in reader
3. **Detect Card**: Card → Detect Card (or press F5)
4. **Authenticate**: Card → Authenticate (enter 8-digit ADM1 key)
5. **Program Card**: Use Manual Card Editor for single cards, or Batch → Start Batch Programming for multiple cards
6. **Verification**: Automatic verification after programming reads back IMSI, ICCID, and MNC length

#### CSV Format:
```csv
IMSI,ICCID,Ki,OPc,ALGO_2G,ALGO_3G,ALGO_4G5G,MNC_LENGTH,USE_OPC
001010000000001,8988211000000000001,00112233445566778899AABBCCDDEEFF,ABCDEF0123456789ABCDEF0123456789,MILENAGE,MILENAGE,MILENAGE,2,1
```

**Basic Columns**:
- `IMSI`: 15 digits
- `ICCID`: 19-20 digits
- `Ki`: 32 hex characters (16 bytes)
- `OPc`: 32 hex characters (for MILENAGE)
- `ALGO_2G`, `ALGO_3G`, `ALGO_4G5G`: COMP128v1/v2/v3, MILENAGE, SHA1-AKA, XOR, XOR-2G, TUAK
- `MNC_LENGTH`: 1 or 2
- `USE_OPC`: 1 (use OPc) or 0 (use OP)

**Network Selection Columns** (CRITICAL for network registration):
- `HPLMN`: Home PLMN (5-6 digits: MCC + MNC, e.g., "24001" for Sweden/Telia, "310410" for USA/AT&T)
  - **This is REQUIRED** - without HPLMN, the card cannot register on any network!
- `OPLMN_ACT`: Operator PLMN list with Access Technology (optional, format: "PLMN:ACT,PLMN:ACT")

**5G SUCI Columns** (required for 5G SA networks with privacy):
- `ROUTING_INDICATOR`: 4-digit hex routing indicator (default: "0000")
- `PROTECTION_SCHEME_ID`: Concealment scheme - 0 (Null), 1 (ProfileA/ECIES), 2 (ProfileB)
- `HNET_PUBKEY_ID`: Home network public key identifier (1-255)
- `HNET_PUBKEY`: Home network public key (64 hex characters / 32 bytes for ProfileA)

⚠️ **5G SUCI Implementation Note**: The GUI writes 5G SUCI parameters to card files (EF.SUCI_Calc_Info, EF.Routing_Indicator, EF.UST). For production 5G SA deployments requiring advanced TLV encoding or pySim-specific features, consider using pySim-shell.py directly (see example_5g_batch_programmer.py for reference implementation)

**Advanced Columns** (optional):
- Milenage: `MILENAGE_R1`-`R5`, `MILENAGE_C1`-`C5`
- TUAK (SJA5 only): `TUAK_RES_SIZE`, `TUAK_MAC_SIZE`, `TUAK_CKIK_SIZE`, `TUAK_NUM_KECCAK`
- SQN: `SQN_IND_SIZE_BITS`, `SQN_CHECK_ENABLED`

### Command-Line Tools

#### Program sysmoUSIM-SJS1:
```bash
./sysmo-usim-tool.sjs1.py \
  -a 76510072 \
  --set-imsi 001010000000001 \
  --set-iccid 8988211000000000001 \
  --set-ki 00112233445566778899AABBCCDDEEFF \
  --set-opc ABCDEF0123456789ABCDEF0123456789
```

#### Program sysmoISIM-SJA2/SJA5:
```bash
./sysmo-isim-sja2-tool.py \
  -a 76510072 \
  --set-imsi 001010000000001 \
  --set-iccid 8988211000000000001 \
  --set-ki 00112233445566778899AABBCCDDEEFF \
  --set-opc ABCDEF0123456789ABCDEF0123456789 \
  --set-auth MILENAGE MILENAGE MILENAGE
```

## Validation & Verification

### Automatic Verification
After programming each card, the system automatically:
1. Reads back **IMSI** from the card
2. Reads back **ICCID** from the card
3. Reads back **MNC length** from EF_AD file
4. Compares with expected values from CSV
5. Reports any mismatches

### What Can Be Verified?
✅ **Readable** (verified automatically):
- IMSI
- ICCID
- MNC length

⚠️ **Write-only** (cannot be read back for security):
- Ki (authentication key)
- OPc/OP (operator variant)
- Milenage R/C parameters
- Algorithm settings

### Manual Verification
Use the GUI's **Manual Card Editor**:
1. Card → 📝 Manual Card Editor
2. Click "Read from Card"
3. View current card parameters
4. Compare with expected configuration

### Testing Authentication
The best validation for Ki/OPc is successful authentication:
```bash
# Test with osmo-hlr or your HSS
# Successful authentication confirms Ki/OPc are correct
```

## Keyboard Shortcuts (GUI)

- `Ctrl+O`: Load CSV
- `Ctrl+S`: Save CSV
- `Ctrl+D` or `F5`: Detect Card

## Troubleshooting

### Card Reader Not Detected
```bash
# Check pcscd is running
systemctl status pcscd

# List readers
pcsc_scan

# Restart pcscd if needed
sudo systemctl restart pcscd
```

### "No module named 'smartcard'"
```bash
# Install pyscard
sudo apt-get install python3-pyscard
# OR
pip3 install pyscard
```

### "No card detected"
1. Ensure card is fully inserted
2. Check reader LED is on
3. Try removing and reinserting card
4. Run `pcsc_scan` to verify card is detected by PC/SC

### Authentication Failed
- Verify ADM1 key is correct (8 digits)
- Check remaining attempts: Card locks after 3 failed attempts
- Each card has a unique ADM1 key (printed on card carrier)

### GUI Won't Start - "No module named 'tkinter'"
```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# macOS
brew install python-tk@3.12
```

## Development

### Project Structure
```
sysmo-usim-tool/
├── gui_main.py              # GUI entry point
├── managers/                # Business logic
│   ├── card_manager.py      # Card I/O operations
│   ├── csv_manager.py       # CSV parsing
│   └── backup_manager.py    # Backup/restore
├── widgets/                 # GUI components
│   ├── card_status_panel.py
│   ├── csv_editor_panel.py
│   └── progress_panel.py
├── dialogs/                 # Modal dialogs
│   ├── card_editor.py       # Manual card editor
│   └── adm1_dialog.py       # ADM1 input
├── utils/                   # Utilities
│   ├── validators.py        # Data validation
│   └── card_detector.py     # ATR-based detection
└── [CLI tools]              # Original command-line tools
```

## Security Notes

- **ADM1 Keys**: Never commit ADM1 keys to version control
- **Ki/OPc**: Keep authentication keys secure - they cannot be read back from cards
- **Backups**: Store JSON backups in a secure location
- **Card Locks**: Cards lock after 3 failed ADM1 attempts (irreversible!)

## License

This project is open source. See individual file headers for copyright information.

## Support & Issues

Report issues at: https://github.com/SeJohnEff/sysmo-usim-tool/issues

## Version History

### v1.2 (2026-02-08)
- ✨ Modern macOS-like user interface
- ✨ Improved typography and spacing
- ✨ Color-coded status indicators
- ✨ Enhanced button styles with clear visual hierarchy
- ✨ Better readability with increased padding and modern fonts

### v1.1 (2026-02-08)
- ✨ PLMN (Public Land Mobile Network) programming support
- ✨ 5G SUCI (Subscription Concealed Identifier) support
- ✨ Network selection configuration (HPLMN, OPLMN)
- ✨ Access Technology flags for 2G/3G/4G/5G
- 📚 Added example_5g_batch_programmer.py reference implementation

### v1.0 (2026-02-08)
- ✨ New GUI application with batch programming
- ✨ CSV import/export
- ✨ Auto-detection of card types (SJA2/SJA5/SJS1)
- ✨ Automatic verification after programming
- ✨ Manual card editor with read/write
- ✨ Progress tracking and statistics
- ✨ TUAK support for 5G (SJA5)
- 🐛 Fixed card status refresh after authentication
- 📚 Comprehensive installation documentation
