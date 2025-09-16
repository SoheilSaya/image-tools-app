# Ubuntu to Windows EXE Build Process Documentation

## What We Built
- **Input**: Python PyQt6 application on Ubuntu Linux
- **Output**: Standalone Windows .exe file that runs on any Windows 10/11 machine
- **Tools Used**: GitHub Actions + PyInstaller + Wine-free approach

## Project Structure
```
image-tools-app/
├── app.py                          # Main Python application (merged tabs)
├── app.spec                        # PyInstaller configuration
├── Vazir-*.ttf                     # Persian/Farsi font files
├── requirements.txt                # Python dependencies
├── README.md                       # Project documentation
└── .github/workflows/build-windows.yml  # GitHub Actions build script
```

## Step-by-Step Process

### 1. Application Development
- **Language**: Python 3.11
- **GUI Framework**: PyQt6
- **Features**: 
  - Tab 1: Address Label Maker (Persian/Farsi support)
  - Tab 2: Image Cropper (34mm x 34mm with PDF output)
- **Dependencies**: PyQt6, Pillow, ReportLab

### 2. GitHub Repository Setup
- **Created repository**: https://github.com/soheilsaya/image-tools-app
- **Authentication**: Personal Access Token (GitHub no longer accepts passwords)
- **Token permissions**: `repo` and `workflow` scopes

### 3. Build Configuration

#### PyInstaller Spec File (`app.spec`)
- **Purpose**: Detailed build configuration for professional EXE
- **Key settings**:
  - `console=False`: No black command window
  - `upx=True`: Compress EXE for smaller size
  - `datas=[...]`: Bundle font files with EXE
  - `hiddenimports=[...]`: Force include modules PyInstaller might miss
  - `excludes=[...]`: Remove bloat (tkinter, matplotlib, etc.)

#### GitHub Actions Workflow (`.github/workflows/build-windows.yml`)
- **Trigger**: Automatic build on every push to main branch
- **Environment**: GitHub's free Windows servers
- **Process**:
  1. Checkout code from repository
  2. Install Python 3.11
  3. Install dependencies (PyQt6, Pillow, ReportLab, PyInstaller)
  4. Run PyInstaller with spec file
  5. Upload resulting EXE as downloadable artifact

### 4. Common Issues and Solutions

#### Issue 1: Git Authentication
- **Problem**: GitHub rejected password authentication
- **Solution**: Created Personal Access Token
- **Token URL**: https://github.com/settings/tokens

#### Issue 2: Repository Access
- **Problem**: "403 Write access denied" 
- **Solution**: Repository didn't exist yet, created via GitHub web interface

#### Issue 3: Git Merge Conflict
- **Problem**: GitHub had README.md, local repo had different files
- **Solution**: `git push --force` to overwrite GitHub's files

#### Issue 4: Build Failed - Icon Not Found
- **Problem**: PyInstaller looked for non-existent `icon.ico`
- **Solution**: Removed icon reference from spec file

#### Issue 5: Missing Fonts in Windows EXE
- **Problem**: Vazir TTF fonts not bundled with executable
- **Solution**: Added font files to `datas` section in spec file

### 5. Build Process Timeline
- **Code push**: ~30 seconds
- **GitHub Actions startup**: ~2 minutes  
- **Dependencies installation**: ~3 minutes
- **EXE compilation**: ~5 minutes
- **Total time**: ~10 minutes per build

### 6. Final Output
- **File**: `ImageTools.exe`
- **Size**: ~50MB (compressed with UPX)
- **Compatibility**: Windows 10/11 (64-bit)
- **Dependencies**: None (fully self-contained)
- **Features**: Persian fonts, image processing, PDF generation

## Commands Reference

### Initial Setup
```bash
mkdir ~/image-tools-github
cd ~/image-tools-github
# Copy your app.py here
# Create .github/workflows/ directory
# Create app.spec file
```

### Git Operations
```bash
git init
git branch -m main
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/USERNAME/REPO.git
git push -u origin main
```

### Authentication (if needed)
```bash
# Create token at: https://github.com/settings/tokens
# Use token as password when prompted
```

### Force Push (if conflicts)
```bash
git push -u origin main --force
```

### Create Releases
```bash
git tag v1.0
git push origin v1.0
# Creates professional release with download buttons
```

## File Templates

### requirements.txt
```
PyQt6==6.7.0
Pillow==10.3.0
reportlab==4.2.0
pyinstaller==6.3.0
```

### Key Spec File Settings
```python
datas=[
    ('*.ttf', 'fonts'),  # Bundle font files
],
hiddenimports=[
    'PyQt6.QtCore',
    'PyQt6.QtGui', 
    'PyQt6.QtWidgets',
    'PIL.Image',
    'reportlab.pdfgen.canvas',
],
excludes=['tkinter', 'matplotlib', 'numpy', 'scipy'],
console=False,  # No console window
upx=True,       # Compress EXE
```

## Advantages of This Method
1. **No Wine needed** on Ubuntu
2. **Professional build system** using GitHub's infrastructure
3. **Free Windows build servers** (no cost)
4. **Automatic building** on code changes
5. **Version control integration**
6. **Professional distribution** with release pages
7. **Cross-platform development** (develop on Linux, deploy on Windows)

## Download Links
- **Development builds**: https://github.com/USERNAME/REPO/actions
- **Releases**: https://github.com/USERNAME/REPO/releases
- **Repository**: https://github.com/USERNAME/REPO

## Success Metrics
- ✅ Ubuntu Python app → Windows EXE
- ✅ Persian font support maintained
- ✅ No Python installation required on target Windows machines  
- ✅ One-click execution for end users
- ✅ Professional deployment pipeline
- ✅ ~50MB final executable size
- ✅ 10-minute build time per update
