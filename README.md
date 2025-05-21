
# BT1 GUI Encrypt Tool

## Overview

BT1 GUI Encrypt Tool is a versatile file encryption and compression tool with a GUI. It supports packing files into the `.bt1` format, unpacking them, and managing encryption settings like passwords and salts. This tool is compatible with both Linux and Windows.

### Features:
- **Packing**: Compress and encrypt files into a `.bt1` format.
- **Unpacking**: Decompress and decrypt `.bt1` files back to their original form.
- **Settings**: Configure password, salt (in hex format), and dark mode.
- **Cross-platform support**: Works on both Linux and Windows systems.
- **Dark Mode**: Toggle dark mode for a more comfortable UI experience.

---

## Requirements

To run the BT1 GUI Encrypt Tool, you'll need the following libraries:

### Python Libraries:
1. **PyQt5**: For building the graphical user interface.
2. **Cryptography**: For AES and ChaCha20 encryption.
3. **zlib**: For file compression.
4. **os, json, struct**: For file handling and configuration.
5. **random, hashlib**: For generating cryptographic keys.
6. **shutil**: For file management operations.

### Installation Steps

Follow these steps to install all required dependencies in one go. You can either use `pip` or install the necessary libraries manually.

### Step 1: Install Python
Make sure you have Python 3.x installed on your machine. You can check if Python is installed with the following command:

```bash
python --version
```

If Python is not installed, download and install it from [Python's official website](https://www.python.org/downloads/).

### Step 2: Install the Required Libraries

You can install all required libraries using the following `pip` command:

```bash
pip install PyQt5 cryptography zlib
```

Alternatively, you can install dependencies one by one:

```bash
pip install PyQt5
pip install cryptography
pip install zlib
```

### Step 3: Download and Use the BT1 GUI Tool
1. Clone the repository or download the source code.
2. Make sure all files are in the same directory.
3. Run the application:

```bash
python bt1_gui.py
```

---

## Technical Specifications

### Module Information:

- **Encryption Algorithm**: 
  - **AES-192** (for encrypting files with the `M25` encryption algorithm).
  - **ChaCha20-Poly1305** (used for stream encryption in `M25`).

- **Packing Process**: 
  1. Files are first compressed using `zlib`.
  2. The resulting compressed data is encrypted using `M25`.
  3. The `.bt1` file format is created with metadata, including file sizes and encryption information.

- **Unpacking Process**:
  1. The `.bt1` file is decrypted using `M25`.
  2. The original compressed data is extracted.
  3. The data is decompressed back into its original form.

- **Salt**: 
  - Salt is used to derive the encryption key. The salt is configurable and stored in the `.bt1config.json` file in hexadecimal format.

- **Password**: 
  - The password is used for encryption/decryption. It is also configurable and stored in the `.bt1config.json` file.

---

## How to Fork and Modify

### Forking the Project

1. Go to the [BT1 GUI GitHub repository](https://github.com/yourusername/bt1gui).
2. Click on the **Fork** button in the top-right corner.
3. After forking, clone the repository to your local machine:

   ```bash
   git clone https://github.com/yourusername/bt1gui.git
   ```

4. Navigate to the directory of the project:

   ```bash
   cd bt1gui
   ```

### Modifying the Project

You can make changes to the following areas:

- **UI Modifications**:
  - Customize the appearance of the interface (e.g., change themes or modify layout).
  - Add additional features like more encryption algorithms or settings.

- **Functionality Changes**:
  - Modify the packing or unpacking logic to add new compression algorithms or encryption methods.
  - Add support for other file formats or improve error handling.

### Submitting Changes

1. After making your changes, commit them:

   ```bash
   git add .
   git commit -m "Describe your changes here"
   ```

2. Push the changes to your fork:

   ```bash
   git push origin main
   ```

3. Open a pull request (PR) on GitHub from your forked repository to the original repository to submit your changes.

---

## Example Usage

### Pack Files

1. Click on the **Pack Files** tab.
2. Choose the input files you want to encrypt and compress.
3. Select the output `.bt1` file location.
4. Click the **Pack File** button to start the process.

### Unpack Files

1. Click on the **Unpack** tab.
2. Select the `.bt1` file you want to decrypt.
3. Choose the destination folder to store the unpacked files.
4. Click the **Unpack** button to start the process.

### Settings

1. Set your password and salt in the **Settings** tab.
2. Toggle **Dark Mode** on or off as desired.
3. Save the settings for future use.

---

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

---

## Contact

If you have any questions or need further assistance, feel free to open an issue on GitHub or contact the maintainer at `youremail@example.com`.

---

## Acknowledgments

- **PyQt5** for creating the cross-platform GUI.
- **Cryptography** for providing strong encryption algorithms.
- **zlib** for efficient file compression.

---

This README should serve as a comprehensive guide for installing, modifying, and using the BT1 GUI Encrypt Tool. It includes all necessary dependencies, steps for contributing, and details on how the module works.
