import customtkinter as ctk
from PIL import Image

class VersionWin(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title('MPRUN Version Info')
        self.iconbitmap('logos and icons/MPRUN_icon.ico')
        self.geometry('500x300')
        self.resizable(False, False)

        self.create_ui()

    def create_ui(self):
        # App image and label
        iog = ctk.CTkImage(light_image=Image.open("logos and icons/MPRUN_logo_rounded_corners_version.png"),
                       dark_image=Image.open("logos and icons/MPRUN_logo_rounded_corners_version.png"),
                       size=(80, 80))
        mprun_img_label = ctk.CTkLabel(self, image=iog, text='')
        mprun_img_label.place(x=20, y=20)

        label = ctk.CTkLabel(self, text='''
1.0.0

Copyright © K-TECH Industries 2024, All rights reserved.

If you encounter any issues or have suggestions for improvements, contact us at:
ktechindustries2019@gmail.com

Your input helps us make MPRUN even better.

Thank you for using MPRUN!''', justify='left')

        label.place(relx=0, anchor='w')
        label.place(x=20, y=190)



if __name__ == '__main__':
    app = VersionWin()
    app.mainloop()
