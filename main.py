import sys
import string
import random
import nltk
nltk.download('words')
from nltk.corpus import words
from PyQt5.QtWidgets import QApplication, QMainWindow
from SimplePasswordGen import Ui_MainWindow
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from datetime import datetime

SIMPLE_WORD_LIST = words.words()

class PasswordGenerator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Set slider ranges (customize if needed)
        self.ui.numCharSlider.setRange(4, 64)
        self.ui.numComplexSlider.setRange(1, 10)

        # Initialize text displays
        self.ui.numChar.setText("4")
        self.ui.numComplex.setText("1")

        # Connect sliders to value display
        self.ui.numCharSlider.valueChanged.connect(self.updateNumChar)
        self.ui.numComplexSlider.valueChanged.connect(self.updateComplexity)

        # Connect button to generation function
        self.ui.generatePushButton.clicked.connect(self.generatePassword)

        # Connect the Save button to function
        self.ui.actionSave.triggered.connect(self.savePasswordToFile)

        # Generate log of passwords generated
        self.generated_passwords = []

        # Clear Password Log
        self.ui.clearPushButton.clicked.connect(self.clearPasswordLog)

    def clearPasswordLog(self):
        self.ui.passLog.clear()  # Clear the log viewer
        self.ui.password.clear()  # Clear the main password display
        self.generated_passwords.clear()  # Clear the list used for saving

    def savePasswordToFile(self):
        if not self.generated_passwords:
            QMessageBox.warning(self, "Nothing to Save", "No passwords have been generated yet.")
            return

        # Let user pick filename
        default_name = f"password_{datetime.today().strftime('%Y-%m-%d')}.txt"
        selected_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Passwords",
            default_name,
            "Text Files (*.txt);;All Files (*)"
        )

        if not selected_path:
            return  # User canceled

        if not selected_path.lower().endswith(".txt"):
            selected_path += ".txt"

        try:
            with open(selected_path, 'a') as f:
                for pw in self.generated_passwords:
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    f.write(f"[{timestamp}] {pw}\n")

            QMessageBox.information(self, "Saved",
                                    f"{len(self.generated_passwords)} passwords saved to:\n{selected_path}")
            self.generated_passwords.clear()  # Optional: clear after saving
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save file:\n{str(e)}")

    def updateNumChar(self, value):
        self.ui.numChar.setText(str(value))

    def updateComplexity(self, value):
        self.ui.numComplex.setText(str(value))

    def generatePassword(self):
        length = self.ui.numCharSlider.value()
        complexity = self.ui.numComplexSlider.value()

        use_words = self.ui.wordCheckBox.isChecked()
        use_digits = self.ui.numCheckBox.isChecked()
        use_punct = self.ui.punCheckBox.isChecked()

        password = ""

        if use_words:
            filtered_words = [w.lower() for w in SIMPLE_WORD_LIST if 2 <= len(w) <= (length - 1) and w.isalpha()]
            max_attempts = 1000
            attempts = 0

            while attempts < max_attempts:
                attempts += 1
                temp_pass = []
                total_len = 0
                digit_used = False
                punct_used = False

                while total_len < length:
                    word = random.choice(filtered_words)
                    modified_word = word

                    # Decide what kind of special char (only one per word)
                    special_char = ''
                    special_type = None  # 'digit' or 'punct'

                    if use_digits and not digit_used:
                        special_char = random.choice(string.digits)
                        special_type = 'digit'
                        digit_used = True
                    elif use_punct and not punct_used:
                        special_char = random.choice(string.punctuation)
                        special_type = 'punct'
                        punct_used = True
                    elif (use_digits or use_punct) and random.random() < 0.5:
                        if use_digits:
                            special_char = random.choice(string.digits)
                            special_type = 'digit'
                        elif use_punct:
                            special_char = random.choice(string.punctuation)
                            special_type = 'punct'

                    # Apply special char if chosen
                    if special_char:
                        if random.choice([True, False]):
                            modified_word = special_char + word
                        else:
                            modified_word = word + special_char

                    if total_len + len(modified_word) > length:
                        break

                    temp_pass.append(modified_word)
                    total_len += len(modified_word)

                # Validate that required specials were included
                if total_len == length and \
                        (not use_digits or digit_used) and \
                        (not use_punct or punct_used):
                    password = ''.join(temp_pass)
                    break

            if not password:
                self.ui.password.setText("Couldn't build a valid password with required components.")
                return

            # Apply complexity: random uppercase letters
            if complexity >= 3:
                password = ''.join(
                    c.upper() if random.random() < complexity / 10 else c for c in password
                )

        else:
            # Char-only mode
            charset = string.ascii_letters
            if use_digits:
                charset += string.digits
            if use_punct:
                charset += string.punctuation

            password = ''.join(random.choices(charset, k=length))

            # Guarantee number
            if use_digits:
                idx = random.randint(0, length - 1)
                password = password[:idx] + random.choice(string.digits) + password[idx + 1:]

            # Guarantee punctuation
            if use_punct:
                idx = random.randint(0, length - 1)
                password = password[:idx] + random.choice(string.punctuation) + password[idx + 1:]

        # After generating password
        timestamp = datetime.now().strftime("%H:%M:%S")
        entry = f"[{timestamp}] {password}"

        self.ui.password.setText(password)
        self.generated_passwords.append(password)
        self.ui.passLog.append(entry)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PasswordGenerator()
    window.show()
    sys.exit(app.exec_())