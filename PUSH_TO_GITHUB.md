# Push to GitHub Instructions

## 1. Check Current Remote

```bash
git remote -v
```

## 2. Add Your GitHub Remote (Choose ONE option)

### Option A: If you want to replace the origin
```bash
# Remove old origin
git remote remove origin

# Add your GitHub repo as origin
git remote add origin https://github.com/SeJohnEff/sysmo-usim-tool.git
# OR using SSH (if you have SSH keys set up):
git remote add origin git@github.com:SeJohnEff/sysmo-usim-tool.git
```

### Option B: If you want to keep osmocom as origin and add GitHub separately
```bash
# Rename current origin
git remote rename origin osmocom

# Add your GitHub repo
git remote add github https://github.com/SeJohnEff/sysmo-usim-tool.git
# OR using SSH:
git remote add github git@github.com:SeJohnEff/sysmo-usim-tool.git
```

## 3. Push to GitHub

```bash
# If you used Option A (origin = your GitHub):
git push -u origin master

# If you used Option B (separate github remote):
git push -u github master
```

## 4. Verify on GitHub

Go to: https://github.com/SeJohnEff/sysmo-usim-tool

You should see:
- All GUI files in new folders (dialogs/, managers/, widgets/, utils/)
- gui_main.py
- GUI_README.md
- Your commit message

## 5. Create GitHub Repository (if it doesn't exist)

If you get an error about repository not existing:

1. Go to https://github.com/new
2. Create repository named: `sysmo-usim-tool`
3. **Do NOT** initialize with README (we already have files)
4. Click "Create repository"
5. Then run the push command again

## Done!

Your code is now on GitHub and you can:
- Clone it on your iMac
- Share it with others
- Create pull requests
- Track issues
