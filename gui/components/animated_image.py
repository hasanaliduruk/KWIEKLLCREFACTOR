import tkinter as tk
from PIL import Image, ImageTk

class AnimatedImage(tk.Label):
    def __init__(self, parent, image_path, alpha=0, *args, **kwargs):
        self.parent = parent
        self.alpha = alpha
        self.isenter = 0
        try:
            self.pimage = Image.open(image_path)
            self.pimage = self.pimage.convert('RGBA')
        except:
            self.pimage = image_path

        self.datas = self.pimage.getdata()
        self.t_list = []
        new_data = []
        for item in self.datas:
            new_data.append((item[0], item[1], item[2], alpha))
            self.t_list.append((item[0], item[1], item[2], item[3]))
        self.pimage.putdata(new_data)
        self.photo = ImageTk.PhotoImage(self.pimage)
        super().__init__(parent, image=self.photo, *args, **kwargs)
        #self.bind("<Enter>", self.event_arttir)
        #self.bind("<Leave>", self.event_azalt)
    def transparant(self):

        new_data = []
        for item in self.t_list:
            new_data.append((item[0], item[1], item[2], int(item[3]*self.alpha)))
        self.pimage.putdata(new_data)
        self.photo = ImageTk.PhotoImage(self.pimage)

        # Resmi güncelle
        self.config(image=self.photo)
        self.image = self.photo
    # Resmi yeniden boyutlandır
    #resized_image = image.resize(new_size)
    def event_arttir(self, e):
        self.isenter = True
        self.arttir()
    def arttir(self):
        self.transparant()
        self.alpha+=0.01
        if self.alpha <= 1.0 and self.isenter == True:
            if self.alpha >= 1.0:
                self.alpha = 1.0
            self.parent.after(1, self.arttir)


    def event_azalt(self, e):
        self.isenter = False
        self.azalt()
    def azalt(self):
        self.transparant()
        self.alpha-=0.01
        if self.alpha >= 0 and self.isenter == False:
            if self.alpha <= 0.0:
                self.alpha = 0.0
            self.parent.after(1, self.azalt)