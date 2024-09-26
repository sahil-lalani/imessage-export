# iPhone Backup Decryption and iMessage Extractor

This project provides a Python script to decrypt an iPhone backup and extract iMessage data along with contacts. It then processes this data and saves it in a more accessible JSON format.

## Features

- Decrypt iPhone backup using a provided passphrase
- Extract iMessage and contacts data from the backup
- Process and combine message data with contact information
- Convert Apple's timestamp format to ISO 8601
- Save extracted data as JSON files

## Requirements

- Python 3.x
- iphone_backup_decrypt library

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/sahil-lalani/imessage-extractor.git
   cd imessage-extractor
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Ensure you have a valid iPhone backup on your computer.

2. Update the `backup_path` in the `decrypt_backup()` function to point to your iPhone backup location:
   - Windows: `C:\Users\[username]\Apple\MobileSync\Backup\[device-hash]`
   - macOS: `/Users/[username]/Library/Application Support/MobileSync/Backup/[device-hash]`

3. Run the script:
   ```bash
   python main.py
   ```

4. When prompted, enter the passphrase for your encrypted iPhone backup.

5. The script will generate three files:
   - `imessage_data.json`: Contains extracted iMessage data
   - `contacts.json`: Contains extracted contact information
   - `imessage.sqlite`: Raw SQLite database file for iMessages
   - `contacts.sqlite`: Raw SQLite database file for contacts

## Output

The `imessage_data.json` file will contain an array of message objects, each with the following structure:

```json
{
    "id": 123456,
    "text": "Message content",
    "date": "2023-04-20T12:34:56.789000",
    "contact": "John Doe",
    "is_from_me": false
}
```


## Notes

- This script is designed for personal use and should be used responsibly and in compliance with applicable laws and regulations.
- Always ensure you have the right to access and decrypt the backup data.

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.