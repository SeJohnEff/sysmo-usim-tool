# Testing GUI on Ubuntu iMac

## 1. On Your M4 MacBook (Push to GitHub)

Follow instructions in [PUSH_TO_GITHUB.md](PUSH_TO_GITHUB.md)

## 2. On Your Ubuntu iMac (Clone and Setup)

### Clone from GitHub
```bash
cd ~
git clone https://github.com/SeJohnEff/sysmo-usim-tool.git
cd sysmo-usim-tool
```

### Verify Dependencies
```bash
# Check Python
python3 --version
# Should show: Python 3.12.3

# Check tkinter
python3 -c "import tkinter; print('✓ tkinter OK')"

# Check pyscard
python3 -c "import smartcard; print('✓ pyscard OK')"

# Check card reader
pcsc_scan
# Should detect: HID Global OMNIKEY 3x21
# Should show your SJA5 card if inserted
```

## 3. Launch GUI

```bash
cd ~/sysmo-usim-tool
python3 gui_main.py
```

## 4. Test Features

### A. Test Manual Card Editor

1. **Menu → Card → 📝 Manual Card Editor**
2. You'll see two tabs: "Basic Parameters" and "Advanced Parameters"

#### Test Read from Card (if card is inserted):
1. Insert your SJA5 card
2. In main window: Click "Detect Card" → "Authenticate" (with correct ADM1!)
3. In Card Editor: Click **"📖 Read from Card"**
4. Should populate: IMSI, ICCID, MNC_LENGTH
5. Ki and OPc cannot be read (security)

#### Test Manual Entry:
1. Enter values in fields (watch for ✓/✗ validation indicators)
2. Fill required fields:
   - IMSI: 15 digits
   - ICCID: 19-20 digits
   - Ki: 32 hex characters
   - OPc: 32 hex characters

#### Test Save to File:
1. Click **"💾 Save to File"**
2. Choose location: e.g., `~/my_card_config.json`
3. Opens in JSON format

#### Test Load from File:
1. Click **"📂 Load from File"**
2. Select your saved JSON file
3. All fields populate with validation

#### Test Write to Card (⚠️ CAUTION!):
1. **ONLY IF** you have correct ADM1 and want to program
2. Click **"✍️ Write to Card"**
3. Confirms before writing
4. Programs all parameters to card

### B. Test CSV Batch Loading

1. **File → Load CSV**
2. Select `test_cards.csv` (or create your own)
3. Table shows all cards with validation
4. Errors highlighted in red

### C. Test Card Detection

1. Insert your SJA5 card
2. Click **"Detect Card"** (or press F5)
3. Should show:
   - Status: Green indicator
   - Card Type: "sysmoISIM-SJA5"
   - ATR detected

### D. Test Authentication (⚠️ CAUTION!)

**ONLY IF YOU HAVE THE CORRECT ADM1 KEY!**

1. Click **"Authenticate"**
2. Dialog shows remaining attempts (should be 3)
3. Enter 8-digit ADM1 key
4. If correct: Green status, "Authenticated"
5. If wrong: **CARD WILL LOCK AFTER 3 FAILURES!**

## 5. File Operations in Card Editor

The card editor can save/load individual card configs as JSON:

### Example Saved File Format
```json
{
  "version": "1.0",
  "type": "card_configuration",
  "config": {
    "IMSI": "001010000000001",
    "ICCID": "8988211000000000001",
    "Ki": "00112233445566778899AABBCCDDEEFF",
    "OPc": "ABCDEF0123456789ABCDEF0123456789",
    "ALGO_2G": "MILENAGE",
    "ALGO_3G": "MILENAGE",
    "ALGO_4G5G": "MILENAGE",
    "MNC_LENGTH": "2"
  }
}
```

### Use Cases

**Scenario 1: Backup Single Card**
1. Authenticate with card
2. Open Card Editor
3. Read from Card
4. Save to File: `backup_card1.json`

**Scenario 2: Program Multiple Cards with Same Config**
1. Create config in Card Editor
2. Save to File: `standard_config.json`
3. For each card:
   - Insert card → Authenticate
   - Card Editor → Load File
   - Modify IMSI (increment last digits)
   - Write to Card

**Scenario 3: Test Configuration Before Batch**
1. Create config in Card Editor
2. Validate all fields (check for ✓ marks)
3. Save to File
4. Add to CSV for batch programming

## 6. Validation Features

### Real-time Validation
- ✓ Green checkmark = Valid
- ✗ Red X = Invalid
- Gray = Empty (optional field)

### Validated Fields
- IMSI: Must be 15 digits
- ICCID: Must be 19-20 digits
- Ki: Must be 32 hex chars (or 64 for TUAK 256-bit)
- OPc: Must be 32 hex chars (or 64 for TUAK)
- Algorithms: Must match valid algorithm names
- MNC_LENGTH: Must be 1, 2, or 3
- Milenage R: 2 hex chars each
- Milenage C: 32 hex chars each
- TUAK params: Specific allowed values

### Status Bar
Bottom of Card Editor shows:
- "✓ All validations passed" (green) = Ready to write
- "❌ X validation error(s)" (red) = Fix errors first
- "⚠️ Missing required fields" (orange) = Fill required fields

## 7. Safety Features

### ADM1 Protection
- Shows remaining attempts
- Warns if < 3 attempts
- Requires confirmation for risky operations
- Force option only if you're SURE

### Write Protection
- Validates ALL fields before writing
- Confirms write operation
- Shows what will be written
- Cannot write without authentication

### Backup Recommended
- Always backup before programming
- Use Card Editor "Read from Card" → "Save to File"
- Or use main window "Backup Current Card"

## 8. Troubleshooting

### GUI Won't Start
```bash
# Install tkinter if missing
sudo apt-get install python3-tk

# Check for errors
python3 gui_main.py
```

### Card Not Detected
```bash
# Restart pcscd
sudo systemctl restart pcscd

# Check reader
pcsc_scan
```

### Authentication Fails
- **STOP immediately!**
- Verify ADM1 from card documentation
- Check remaining attempts in dialog
- Do NOT guess - card locks after 3 failures

### Validation Errors
- Hover over field to see error message
- Check bottom status bar
- Red ✗ indicator shows which field has error
- Fix and watch for green ✓

## 9. What to Test

✅ **Safe to Test:**
- GUI opens and displays correctly
- Load CSV files
- Card detection (no auth needed)
- Manual editor field entry
- Validation indicators
- Save/load config files
- File dialogs

⚠️ **Test with Caution:**
- Authentication (only with correct ADM1!)
- Read from card (requires auth)

❌ **DO NOT Test Without Correct ADM1:**
- Write to card
- Batch programming
- Any authentication attempts

## 10. Expected Behavior

### Card Editor Layout
```
┌─────────────────────────────────────────────┐
│ Card Editor - Read/Write Single Card       │
├─────────────────────────────────────────────┤
│ [Basic Parameters] [Advanced Parameters]    │
│                                             │
│ IMSI:           [_______________] ✓ 15dig   │
│ ICCID:          [_______________] ✓ 19-20   │
│ Ki:             [_______________] ✓ 32hex   │
│ OPc:            [_______________] ✓ 32hex   │
│ ALGO_2G:        [MILENAGE______] ✓         │
│ ALGO_3G:        [MILENAGE______] ✓         │
│ ALGO_4G5G:      [MILENAGE______] ✓         │
│ MNC_LENGTH:     [2_____________] ✓ 1-3     │
│ USE_OPC:        [1_____________] ✓ 0or1    │
│                                             │
├─────────────────────────────────────────────┤
│ [Card Operations]  [File Operations]       │
│ [📖 Read]  [✍️ Write]  [📂 Load]  [💾 Save]   │
│                                     [Close] │
│ ✓ All validations passed                   │
└─────────────────────────────────────────────┘
```

## Success Checklist

- [ ] GUI launches without errors
- [ ] Card detected and shows "sysmoISIM-SJA5"
- [ ] CSV loads and displays in table
- [ ] Card Editor opens and shows all fields
- [ ] Validation indicators work (✓/✗)
- [ ] Can save card config to JSON file
- [ ] Can load card config from JSON file
- [ ] (If authenticated) Can read card data
- [ ] Log panel shows all operations

## Next Steps

Once everything works:
1. Find correct ADM1 key for your cards
2. Test authentication with correct key
3. Test read from card
4. Create backup before any writes
5. Test write to single card
6. Try batch programming

## Support

If you encounter issues:
- Check GUI log panel (bottom right)
- Run `pcsc_scan` to verify hardware
- Check Python/dependency versions
- Review error messages in terminal
