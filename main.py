from PyQt5 import QtWidgets
from PyQt5.QtGui import QPixmap, QPainter, QPen, QFont
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QTimer
import sys, datetime, random

#Notes % 12 gives value
note_names_flats = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']
flat_offsets = [0, 20, 20, 40, 40, 60, 80, 80, 100, 100, 120, 120]
note_names_sharps = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
sharp_offsets = [0, 0, 20, 20, 40, 60, 60, 80, 80, 100, 100, 120]
#if 1,3,6,8,10 then black key (flat or sharp)
black_keys = [1, 3, 6, 8, 10]
flat_scales = [1,3,5,6,9,10]
sharp_scales = [2,4,7,8,11]

class MyWindow(QMainWindow):


    def __init__(self):
        #init UI buttons and keys
        super(MyWindow, self).__init__()
        self.setGeometry(200, 200, 1200, 1000)
        self.setWindowTitle("Piano Learning Tool")
        self.initUI()
        self.note_buttons = self.initKeys()

        #change mode
        self.mode_change = False

        #init variables
        self.timer = QTimer()
        self.learn_timer = QTimer()
        self.color_timer = QTimer()
        self.sound_timer = QTimer()
        #self.scale_timer = QTimer()

        #trigger to load new note, which button/note value was pressed, note to compare to
        self.button_pressed = False
        self.note_pressed = None
        self.note_to_press = None
        self.note_array_to_press = []

        #quiz-variables
        self.learning_counter = 0
        self.note_quiz_score = 0
        self.note_quiz_counter = 0
        self.note_quiz_length = 5
        self.quiz_notes = []
        self.quiz_played_notes = []

        self.notes_spawned = []
        self.accidentals_spawned = []
        self.scale_position = 0
        self.scale_all_notes = []
        self.scale_played_notes = []

    def initUI(self):
        # self.label = QtWidgets.QLabel(self)
        # self.label.setText("my first label")
        # self.label.move(50, 50)

        self.treble_path = "images/treble2.png"
        self.bass_path = "images/bass2.png"


        image_treble = QLabel(self)
        image_treble.setGeometry(50, 50, 92, 250)
        pixmap_treble = QPixmap(self.treble_path)
        image_treble.setPixmap(pixmap_treble)
        image_bass = QLabel(self)
        image_bass.setGeometry(50, 320, 92, 109)
        pixmap_bass = QPixmap(self.bass_path)
        image_bass.setPixmap(pixmap_bass)

        # buttons
        self.note_learn_button = QtWidgets.QPushButton(self)
        self.note_learn_button.setText("Note Learn")
        self.note_learn_button.move(25, 650)
        self.note_learn_button.clicked.connect(self.learning_notes)

        self.note_quiz_button = QtWidgets.QPushButton(self)
        self.note_quiz_button.setText("Notes Quiz")
        self.note_quiz_button.move(25, 700)
        self.note_quiz_button.clicked.connect(self.learning_notes_quiz)

        self.help_button = QtWidgets.QPushButton(self)
        self.help_button.setText("Help")
        self.help_button.move(1100, 0)
        self.help_button.clicked.connect(self.help_popup)

        #self.note_scale_button = QtWidgets.QPushButton(self)
        #self.note_scale_button.setText("Learn Scales")
        #self.note_scale_button.move(25, 750)
        #self.note_scale_button.clicked.connect(self.spawn_scale_learn)

        # images that only need once instance
        self.octave_note = QtWidgets.QLabel(self)
        self.octave_note.setFont(QFont('Arial', 24))
        self.octave_note.setText("8va")
        self.octave_note.move(-100, 250)

        self.note_name = QtWidgets.QLabel(self)
        self.note_name.setFont(QFont('Arial', 24))
        self.note_name.setText(note_names_flats[0])
        self.note_name.move(-100, 250)

        self.scale_name = QtWidgets.QLabel(self)
        self.scale_name.setFont(QFont('Arial', 24))
        self.scale_name.setText("t")
        self.scale_name.setGeometry(-100,250,200,50)

        self.scores = QtWidgets.QLabel(self)
        self.scores.setFont(QFont('Arial', 18))
        self.scores.setGeometry(-600, 0, 500, 500)

        self.quized_notes_display = QtWidgets.QLabel(self)
        self.quized_notes_display.setFont(QFont('Arial', 18))
        self.quized_notes_display.setGeometry(-1000, 800, 600, 20)
        self.played_notes_display = QtWidgets.QLabel(self)
        self.played_notes_display.setFont(QFont('Arial', 18))
        self.played_notes_display.setGeometry(-1000, 800, 600, 20)

        self.learn_summary_display = QtWidgets.QLabel(self)
        self.learn_summary_display.setFont(QFont('Arial', 10))
        self.learn_summary_display.setGeometry(130, 415, 500, 500)
        self.learn_summary_display.setText("Click this button to learn notes!")

        self.quiz_summary_display = QtWidgets.QLabel(self)
        self.quiz_summary_display.setFont(QFont('Arial', 10))
        self.quiz_summary_display.setGeometry(130, 465, 500, 500)
        self.quiz_summary_display.setText("Click this button to quiz yourself!")


        self.single_images = [self.octave_note, self.note_name, self.scale_name]
        self.layout = QVBoxLayout()



    def help_popup(self):
        msg = QMessageBox()
        msg.setText("Learn Notes: This button will populate notes onto the staff\n"
                    "as well as the name of the note. This will allow you to learn\n"
                    "what each location on the staff represents. The next note will\n"
                    "not spawn until you choose the correct note.\n\n"
                    "Quiz Notes: This button will start a quiz to allow you to choose\n"
                    "the correct note populated on the staff. There is a counter to keep\n"
                    "track of how well you're doing. If you click on Quiz again you can\n"
                    "restart.")
        msg.exec_()


    def initKeys(self):
        black_key_style = """ 
            QPushButton{
                background-color: black;
                border: 1px solid black}

            QPushButton:hover{
                background-color: cyan;}"""

        white_key_style = """ 
            QPushButton{
                background-color: white;
                border: 1px solid black}

            QPushButton:hover{
                background-color: cyan;}"""

        self.buttonC0 = QtWidgets.QPushButton(self)
        self.buttonC0.setGeometry(100, 875, 40, 100)
        self.buttonC0.setStyleSheet(white_key_style)
        self.buttonC0.clicked.connect(lambda: self.on_button_click(0))

        self.buttonC1 = QtWidgets.QPushButton(self)
        self.buttonC1.setGeometry(380, 875, 40, 100)
        self.buttonC1.setStyleSheet(white_key_style)
        self.buttonC1.clicked.connect(lambda: self.on_button_click(12))

        self.buttonC2 = QtWidgets.QPushButton(self)
        self.buttonC2.setGeometry(660, 875, 40, 100)
        self.buttonC2.setStyleSheet(white_key_style)
        self.buttonC2.clicked.connect(lambda: self.on_button_click(24))

        self.C_keys = [self.buttonC0, self.buttonC1, self.buttonC2]

        self.buttonD0 = QtWidgets.QPushButton(self)
        self.buttonD0.setGeometry(140, 875, 40, 100)
        self.buttonD0.setStyleSheet(white_key_style)
        self.buttonD0.clicked.connect(lambda: self.on_button_click(2))

        self.buttonD1 = QtWidgets.QPushButton(self)
        self.buttonD1.setGeometry(420, 875, 40, 100)
        self.buttonD1.setStyleSheet(white_key_style)
        self.buttonD1.clicked.connect(lambda: self.on_button_click(14))

        self.D_keys = [self.buttonD0, self.buttonD1]

        self.buttonE0 = QtWidgets.QPushButton(self)
        self.buttonE0.setGeometry(180, 875, 40, 100)
        self.buttonE0.setStyleSheet(white_key_style)
        self.buttonE0.clicked.connect(lambda: self.on_button_click(4))

        self.buttonE1 = QtWidgets.QPushButton(self)
        self.buttonE1.setGeometry(460, 875, 40, 100)
        self.buttonE1.setStyleSheet(white_key_style)
        self.buttonE1.clicked.connect(lambda: self.on_button_click(16))

        self.E_keys = [self.buttonE0, self.buttonE1]

        self.buttonF0 = QtWidgets.QPushButton(self)
        self.buttonF0.setGeometry(220, 875, 40, 100)
        self.buttonF0.setStyleSheet(white_key_style)
        self.buttonF0.clicked.connect(lambda: self.on_button_click(5))

        self.buttonF1 = QtWidgets.QPushButton(self)
        self.buttonF1.setGeometry(500, 875, 40, 100)
        self.buttonF1.setStyleSheet(white_key_style)
        self.buttonF1.clicked.connect(lambda: self.on_button_click(17))

        self.F_keys = [self.buttonF0, self.buttonF1]

        self.buttonG0 = QtWidgets.QPushButton(self)
        self.buttonG0.setGeometry(260, 875, 40, 100)
        self.buttonG0.setStyleSheet(white_key_style)
        self.buttonG0.clicked.connect(lambda: self.on_button_click(7))

        self.buttonG1 = QtWidgets.QPushButton(self)
        self.buttonG1.setGeometry(540, 875, 40, 100)
        self.buttonG1.setStyleSheet(white_key_style)
        self.buttonG1.clicked.connect(lambda: self.on_button_click(19))

        self.G_keys = [self.buttonG0, self.buttonG1]

        self.buttonA0 = QtWidgets.QPushButton(self)
        self.buttonA0.setGeometry(300, 875, 40, 100)
        self.buttonA0.setStyleSheet(white_key_style)
        self.buttonA0.clicked.connect(lambda: self.on_button_click(9))

        self.buttonA1 = QtWidgets.QPushButton(self)
        self.buttonA1.setGeometry(580, 875, 40, 100)
        self.buttonA1.setStyleSheet(white_key_style)
        self.buttonA1.clicked.connect(lambda: self.on_button_click(21))

        self.A_keys = [self.buttonA0, self.buttonA1]

        self.buttonB0 = QtWidgets.QPushButton(self)
        self.buttonB0.setGeometry(340, 875, 40, 100)
        self.buttonB0.setStyleSheet(white_key_style)
        self.buttonB0.clicked.connect(lambda: self.on_button_click(11))

        self.buttonB1 = QtWidgets.QPushButton(self)
        self.buttonB1.setGeometry(620, 875, 40, 100)
        self.buttonB1.setStyleSheet(white_key_style)
        self.buttonB1.clicked.connect(lambda: self.on_button_click(23))

        self.B_keys = [self.buttonB0, self.buttonB1]

        self.buttonDb0 = QtWidgets.QPushButton(self)
        self.buttonDb0.setGeometry(127, 875, 26, 50)
        self.buttonDb0.setStyleSheet(black_key_style)
        self.buttonDb0.clicked.connect(lambda: self.on_button_click(1))

        self.buttonDb1 = QtWidgets.QPushButton(self)
        self.buttonDb1.setGeometry(407, 875, 26, 50)
        self.buttonDb1.setStyleSheet(black_key_style)
        self.buttonDb1.clicked.connect(lambda: self.on_button_click(13))

        self.Db_keys = [self.buttonDb0, self.buttonDb1]

        self.buttonEb0 = QtWidgets.QPushButton(self)
        self.buttonEb0.setGeometry(167, 875, 26, 50)
        self.buttonEb0.setStyleSheet(black_key_style)
        self.buttonEb0.clicked.connect(lambda: self.on_button_click(3))

        self.buttonEb1 = QtWidgets.QPushButton(self)
        self.buttonEb1.setGeometry(447, 875, 26, 50)
        self.buttonEb1.setStyleSheet(black_key_style)
        self.buttonEb1.clicked.connect(lambda: self.on_button_click(15))

        self.Eb_keys = [self.buttonEb0, self.buttonEb1]

        self.buttonGb0 = QtWidgets.QPushButton(self)
        self.buttonGb0.setGeometry(247, 875, 26, 50)
        self.buttonGb0.setStyleSheet(black_key_style)
        self.buttonGb0.clicked.connect(lambda: self.on_button_click(6))

        self.buttonGb1 = QtWidgets.QPushButton(self)
        self.buttonGb1.setGeometry(527, 875, 26, 50)
        self.buttonGb1.setStyleSheet(black_key_style)
        self.buttonGb1.clicked.connect(lambda: self.on_button_click(18))

        self.Gb_keys = [self.buttonGb0, self.buttonGb1]

        self.buttonAb0 = QtWidgets.QPushButton(self)
        self.buttonAb0.setGeometry(287, 875, 26, 50)
        self.buttonAb0.setStyleSheet(black_key_style)
        self.buttonAb0.clicked.connect(lambda: self.on_button_click(8))

        self.buttonAb1 = QtWidgets.QPushButton(self)
        self.buttonAb1.setGeometry(567, 875, 26, 50)
        self.buttonAb1.setStyleSheet(black_key_style)
        self.buttonAb1.clicked.connect(lambda: self.on_button_click(20))

        self.Ab_keys = [self.buttonAb0, self.buttonAb1]

        self.buttonBb0 = QtWidgets.QPushButton(self)
        self.buttonBb0.setGeometry(327, 875, 26, 50)
        self.buttonBb0.setStyleSheet(black_key_style)
        self.buttonBb0.clicked.connect(lambda: self.on_button_click(10))

        self.buttonBb1 = QtWidgets.QPushButton(self)
        self.buttonBb1.setGeometry(607, 875, 26, 50)
        self.buttonBb1.setStyleSheet(black_key_style)
        self.buttonBb1.clicked.connect(lambda: self.on_button_click(22))

        self.Bb_keys = [self.buttonBb0, self.buttonBb1]

        all_notes = [self.C_keys, self.Db_keys, self.D_keys, self.Eb_keys, self.E_keys, self.F_keys,
                         self.Gb_keys, self.G_keys, self.Ab_keys, self.A_keys, self.Bb_keys, self.B_keys]

        return all_notes

    def on_button_click(self, value):
        self.note_pressed = value
        self.button_pressed = True
        #self.play_sound((value + 36))


        #returns red if wrong, green if right
        if self.note_to_press is not None:

            #find button to change: %12 is first index of button 2d array, /12 is button
            key_pressed = self.note_buttons[value%12][int(value/12)]

    def spawn_note_images(self):
        self.image_note = QLabel(self)
        note_path = "images/whole_note.png"
        pixmap_note = QPixmap(note_path)
        self.image_note.setPixmap(pixmap_note)
        self.image_note.move(-200, -200)

        self.image_flat = QLabel(self)
        flat_path = "images/flat.png"
        pixmap_flat = QPixmap(flat_path)
        self.image_flat.setPixmap(pixmap_flat)
        self.image_flat.move(-200, -200)

        self.image_sharp = QLabel(self)
        sharp_path = "images/sharp.png"
        pixmap_sharp = QPixmap(sharp_path)
        self.image_sharp.setPixmap(pixmap_sharp)
        self.image_sharp.move(-200, -200)

        return self.image_note, self.image_flat, self.image_sharp

    def paintEvent(self,event):
        painter = QPainter(self)
        painter.setPen(QPen(Qt.black, 3))

        #treble clef
        painter.drawLine(25, 80, 850, 80)
        painter.drawLine(25, 120, 850, 120)
        painter.drawLine(25, 160, 850, 160)
        painter.drawLine(25, 200, 850, 200)
        painter.drawLine(25, 240, 850, 240)
        #bass clef
        painter.drawLine(25, 320, 850, 320)
        painter.drawLine(25, 360, 850, 360)
        painter.drawLine(25, 400, 850, 400)
        painter.drawLine(25, 440, 850, 440)
        painter.drawLine(25, 480, 850, 480)

        #lines above, between, and below grand staff
        painter.setPen(QPen(Qt.black, 1, Qt.DotLine))

        painter.drawLine(50, 40, 850, 40)
        painter.drawLine(50, 0, 850, 0)
        painter.drawLine(50, 280, 850, 280)
        painter.drawLine(50, 520, 850, 520)
        painter.drawLine(50, 560, 850, 560)
        painter.drawLine(50, 600, 850, 600)
        painter.end()

    def learning_notes(self):
        #self.staff_reset()
        #self.timer_reset()

        self.note_pressed = 0
        self.learning_counter = 0
        self.button_pressed = False
        note_array = []


        # fill random notes
        for i in range(0, 250):
            note_array.append(random.randint(21, 108))

        # spawn first note
        self.spawn_note(note_array[0], True)
        self.note_to_press = note_array[0]
        #self.play_sound(note_array[0])

        # create timer to run helper every 0.25 seconds
        self.learn_timer.timeout.connect(lambda: self.learning_notes_helper(note_array))
        self.learn_timer.setInterval(150)
        self.learn_timer.start()

    def learning_notes_helper(self, note):
        # checks every 0.15 seconds, if key pressed
        if self.button_pressed:
            self.button_pressed = False
            if note[self.learning_counter] % 12 == self.note_pressed % 12:
                self.learning_counter += 1
                self.spawn_note(note[self.learning_counter], True)
                print(note[self.learning_counter])
            self.note_to_press = note[self.learning_counter]
            #self.play_sound(note[self.learning_counter])
        if self.learning_counter == 250:
            self.learn_timer.stop()

    def learning_notes_quiz(self):
        self.staff_reset()
        #self.timer_reset()

        self.note_pressed = 0
        self.button_pressed = False
        self.note_quiz_score = 0
        self.note_quiz_counter = 0
        self.quiz_start_time = datetime.datetime.now()
        note_array = []

        quiz_length = QtWidgets.QInputDialog.getInt(
                    self, 'Quiz Length', 'Enter how many notes you want to be quizzed on: ')
        self.note_quiz_length = quiz_length[0]
        #fill random notes
        for i in range(0, self.note_quiz_length):
            note_array.append(random.randint(21, 108))
        self.quiz_notes = note_array

        #spawn first note
        self.spawn_note(note_array[0], False)
        self.note_to_press = note_array[0]

        #disconnect timer when starting new if current timer exists
        #create timer to run helper every 0.1 seconds
        try:
            self.timer.timeout.disconnect()
        except TypeError:
            pass
        self.timer.timeout.connect(lambda: self.learning_notes_quiz_helper(note_array))
        self.timer.setInterval(100)
        self.timer.start()

    #spawns a single note during the note quiz, updates after a note is clicked
    def learning_notes_quiz_helper(self, note):


        #checks every 0.15 seconds, if key pressed
        if self.button_pressed == True:
            self.button_pressed = False



            if note[self.note_quiz_counter] % 12 == self.note_pressed % 12:
                self.note_quiz_score += 1

            self.quiz_played_notes.append(self.note_pressed % 12)
            self.note_quiz_counter += 1

            correct_notes = "Quizzed:"
            played_notes = "Played:  "

            if self.note_quiz_counter >= self.note_quiz_length:
                self.quiz_end_time = datetime.datetime.now()
                self.timer.stop()
                self.staff_reset()

                #calculate time difference to send to microservice
                total_time = self.quiz_end_time - self.quiz_start_time
                seconds = int(total_time.total_seconds())
                microseconds = total_time.total_seconds() - seconds

                new_name = QtWidgets.QInputDialog.getText(
                    self, 'Input Dialog', f'Score: {self.note_quiz_score}! Enter your name: ')

                #Send data to Microservice A
                # self.add_score(
                #     new_name[0],
                #     self.note_quiz_score,
                #     (self.note_quiz_length-self.note_quiz_score),
                #     datetime.timedelta(seconds=seconds, microseconds=microseconds*100))
                # .show_scores()

                # Display goes here
                for i in range(0, self.note_quiz_length):
                    correct_notes += str(note_names_flats[(self.quiz_notes[i] % 12)]) + "  "
                    played_notes += str(note_names_flats[(self.quiz_played_notes[i] % 12)]) + "  "
                self.quized_notes_display.setText(correct_notes)
                self.quized_notes_display.move(200, 800)
                self.played_notes_display.setText(played_notes)
                self.played_notes_display.move(200, 825)



            else:
                self.note_to_press = note[self.note_quiz_counter]
                self.spawn_note(note[self.note_quiz_counter], False)

    def spawn_note(self, note, draw=False):
        #note dimension is 40x40, offset y by -20
        #middle C is line at y-coord 260, notes are 20 units apart. Full octave is 140
        #lowest midi number is 21, y coord is 600
            #at 12 would be 700, but starts at 21
            #midi number div 12 - 1 = octave
            #midi number % 12 is full note, use offset from flat / sharp offset
        #final y coord = 700 - onctave calculation - offset from flats - 20 to offset image

        #if not hasattr(self, 'image_note'):
        #if not hasattr(self, 'image_flat'):
        #if not hasattr(self, 'image_sharp'):


        self.staff_reset()

        image_note, flat_note, sharp_note = self.spawn_note_images()
        self.notes_spawned.append(image_note)
        self.accidentals_spawned.append(flat_note)
        self.accidentals_spawned.append(sharp_note)

        #logic to shift octaves down to be more readable
        semitone_choice = random.randint(0,1)
        if semitone_choice == 0:
            semitone = flat_offsets
        else:
            semitone = sharp_offsets



        if 72 <= note < 84:
            ycoord = 840 - ((int(note / 12) - 1) * 140) - semitone[note % 12] - 20
            self.octave_note.move(500, 50)
            self.octave_note.setText("8va")
        elif 84 <= note < 96:
            ycoord = 980 - ((int(note / 12) - 1) * 140) - semitone[note % 12] - 20
            self.octave_note.move(500, 50)
            self.octave_note.setText("15va")
        elif note >= 96:
            ycoord = 1120 - ((int(note / 12) - 1) * 140) - semitone[note % 12] - 20
            self.octave_note.move(500, 50)
            self.octave_note.setText("22va")
        else:
            ycoord = 700 - ((int(note / 12) - 1) * 140) - semitone[note % 12] - 20
            self.octave_note.move(-500, 50)

        #where to spawn the image note, and if a flat/sharp symbol should be spawned
        image_note.setGeometry(200, ycoord, 40, 40)

        #spawns and sets accidental images if needed
        if (note % 12) in black_keys:
            if semitone_choice == 0:
                flat_note.setGeometry(178, ycoord, 22, 40)
                sharp_note.setGeometry(-500, ycoord, 29, 40)
            else:
                flat_note.setGeometry(-500, ycoord, 22, 40)
                sharp_note.setGeometry(171, ycoord, 29, 40)
        else:
            flat_note.setGeometry(-500, ycoord, 22, 40)
            sharp_note.setGeometry(-500, ycoord, 29, 40)

        #if learning, shows note names
        if draw and semitone_choice == 0:
            self.note_name.setText(note_names_flats[note%12])
            self.note_name.move(250, ycoord-5)
        elif draw and semitone_choice == 1:
            self.note_name.setText(note_names_sharps[note % 12])
            self.note_name.move(250, ycoord-5)


        #show and update gui
        image_note.show()
        flat_note.show()
        sharp_note.show()
        self.update()

    def staff_reset(self):


        if self.notes_spawned:
            for each in self.notes_spawned:
                each.clear()
        if self.accidentals_spawned:
            for each in self.accidentals_spawned:
                each.clear()
        for each in self.single_images:
            each.move(-500, -500)

        self.scores.move(-600, 0)
        self.quized_notes_display.move(200, -2000)
        self.played_notes_display.move(200, -2000)
        #self.scale_all_notes.clear()
        #self.scale_played_notes.clear()


        self.notes_spawned = []
        self.accidentals_spawned = []

    def timer_reset(self):
        self.timer.stop()
        self.learn_timer.stop()
        self.color_timer.stop()
        self.scale_timer.stop()


def window():
    app = QApplication(sys.argv)
    win = MyWindow()

    win.show()
    sys.exit(app.exec_())

window()