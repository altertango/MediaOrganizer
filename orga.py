#!/usr/bin/env python3

#tkinter imports
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox as mbx
from tkinter import filedialog as fd
import ctypes

#other imports
import os
import numpy as np
import cv2
from PIL import ImageTk, Image
from os import listdir, getcwd, walk, mkdir, rename
from os.path import isfile, isdir
from shutil import rmtree, move
from send2trash import send2trash
import time
########################### Functions #############################

#Function to get the names of every file in a given path (mp)
def onlyfiles(mp):
    return [f for f in listdir(mp) if isfile(os.path.join(mp,f))]

#Function to get the names of every folder in a given path (mp)
def onlyfolders(mp):
    return [f for f in listdir(mp) if isdir(os.path.join(mp,f))]

#make a folder
def mk_folder(folder_name):
    path=getcwd()
    if folder_name not in onlyfolders(path):
        mkdir(os.path.join(path,folder_name))


class MyVideoCapture:
    def __init__(self, video_source=0):
        # Open the video source
        self.vid = cv2.VideoCapture(video_source)
        if not self.vid.isOpened():
            raise ValueError("Unable to open video source", video_source)

        # Get video source width and height
        self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)

    def get_frame(self):
        if self.vid.isOpened():
            ret, frame = self.vid.read()
            if ret:
                # Return a boolean success flag and the current frame converted to BGR
                return (ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            else:
                return (ret, None)
        else:
            return (ret, None)

    # Release the video source when the object is destroyed
    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()

########################### GUI ###################################

class Main_app(tk.Frame):

    def __init__(self):
        super().__init__()
        self.initUI()
        
        #other self variables

    
    def initUI(self):
        self.img_types=['jpg','png','bmp','tif','tiff','jpeg','gif']
        self.vid_types=['avi','mp4','mov','wmv','flv','f4v','swf','mkv']
        self.output_paths=[]
        self.frames=[]
        self.labels=[]
        self.entries=[]
        self.buttons=[]
        self.w_w=640
        self.w_h=480
        
        #videocap
        self.vid=0
        self.delay = 15

        
        self.master.title("Media organizer")
        self.last_path=os.getcwd()
        self.style = ttk.Style()
        self.style.theme_use("default")
        frame = ttk.Frame(self, relief=tk.RAISED, borderwidth=1)
        frame.pack(fill=tk.BOTH, expand=True)
        self.pack(fill=tk.BOTH, expand=True)
        
        
        
        label_0_0 =tk.Label(frame,text="Media organizer",font=("bold",13))
        label_0_0.pack(padx=10,pady=30)
        
        label_0_1 =tk.Label(frame,text="Select your input folder:",font=(11))
        label_0_1.pack(padx=10,pady=10)
        path_input=tk.StringVar()
        frame1=tk.Frame(frame)
        label_1 =tk.Label(frame1,text="Input folder", width=30,font=("bold",10))
        label_1.grid(row=1,column=1)
        entry_1=tk.Entry(frame1, width=40, textvariable=path_input)
        entry_1.grid(row=1,column=2)
        browse = ttk.Button(frame1, text="Browse", command=lambda: self.open_dir_form(path_input))
        browse.grid(row=1,column=3,padx=10)    
        
        frame1.pack()
        
        label_0_2 =tk.Label(frame,text="Select your output folder(s):",font=(11))
        label_0_2.pack(padx=10,pady=10)
        
        self.addOutputFolder(frame)

        frame2=tk.Frame(self)
        adOutputButton = ttk.Button(frame2, text="Add output folder", command =lambda: self.addOutputFolder(frame))
        adOutputButton.grid(row=1,column=3, padx=15, pady=15)
        
        okButton = ttk.Button(frame2, text="Go!", command =lambda: self.Go(path_input.get(),[i.get() for i in self.output_paths]))
        okButton.grid(row=1,column=4, padx=15, pady=15)
        frame2.pack()
        #preview = ttk.Button(frame1, text="preview", command=lambda: self.preview(path_sond.get()))
        #preview.grid(row=1,column=4,padx=10) 
        
        
    def Go(self,path_input, outputs):
        for f in self.walk_files(path_input):
            print(f)
            if f.split('.')[-1].lower() in self.img_types or f.split('.')[-1].lower() in self.vid_types:
                out=self.preview(f,outputs)
                if out==-99: send2trash(f)
                elif out==-1: break
                else:
                    move(f,os.path.join(outputs[out],os.path.basename(f)))
        
    def walk_files(self,path):
        files=[]
        for f in walk(path):
            for f2 in [os.path.normpath(os.path.join(f[0],i)) for i in f[2]]:
                files.append(f2)
        return files
        

    def addOutputFolder(self,frame):
        self.output_paths+=[tk.StringVar()]
        row_n=(len(self.output_paths)+1)
        self.frames+=[tk.Frame(frame)]
        self.labels+=[tk.Label(self.frames[-1],text="Output folder "+str(len(self.output_paths)), width=30,font=("bold",10))]
        self.labels[-1].grid(row=row_n,column=1)
        self.entries+=[tk.Entry(self.frames[-1], width=40, textvariable=self.output_paths[row_n-2])]
        self.entries[-1].grid(row=row_n,column=2)
        self.buttons+=[ttk.Button(self.frames[-1], text="Browse", command=lambda: self.open_dir_form(self.output_paths[row_n-2]))]
        self.buttons[-1].grid(row=row_n,column=3,padx=10)  
        self.frames[-1].pack(pady=15, padx=10)
        
        
    def preview(self,f,outputs):
        if f.split('.')[-1] in self.img_types: out=self.previewPic(f,outputs)
        elif f.split('.')[-1] in self.vid_types: out=self.previewVideo(f,outputs)
        else:
            return
        return out

    def open_file_form(self,var,tipo):
        path=self.last_path
        filetypes = (
            (tipo, '*.'+tipo),
            ('All files', '*.*')
        )
        filename = fd.askopenfilename(parent=self,
            title='Abrir CSV',
            initialdir=path,
            filetypes=filetypes)
        var.set(filename)

    def open_dir_form(self,var):
        path=self.last_path
        dirname = fd.askdirectory(parent=self,
            title='Select a directory',
            initialdir=path)
        var.set(dirname)

    def previewVideo(self,f,outputs):
        
        
        self.t = tk.Toplevel(self)
        self.t.geometry('800x600+100+100')
        var0=tk.IntVar()
        self.t.title(f)
        self.t.protocol("WM_DELETE_WINDOW", lambda: var0.set(-1))
        label_0_0 =tk.Label(self.t,text=f,font=("bold",13))
        label_0_0.pack(padx=10,pady=10)
        
        
        #################### video ###################
        self.Vcanvas = tk.Canvas(self.t, width = self.w_w, height = self.w_h)
        self.Vcanvas.pack()
        self.vid = MyVideoCapture(f)



        # After it is called once, the update method will be automatically called every delay milliseconds
        
        self.update()

        #################### video ###################


        
        
        butons=[]
        c=0
        for o in outputs:
            name=o.split('/')[-1]
            if len(name)>=10: name=name[:10]+'...'
            butons+=[ttk.Button(self.t, text=name+' ('+str(c+1)+')', command=lambda c=c: var0.set(c))]
            c+=1
            butons[-1].pack(side=tk.LEFT, padx=5, pady=5)
            
        cancelButton = ttk.Button(self.t, text="Quit", command=lambda: var0.set(-1))
        cancelButton.pack(side=tk.RIGHT, padx=5, pady=5)
        
        delButton = ttk.Button(self.t, text="Delete", command =lambda: var0.set(-99))
        delButton.pack(side=tk.RIGHT, padx=5, pady=5)
        
        self.t.wait_variable(var0)
        self.t.destroy()
        
        return var0.get()


    def update(self):
        # Get a frame from the video source
        ret, frame = self.vid.get_frame()
        if ret:
            im = Image.fromarray(frame)
            width, height = im.size
            if width>self.w_w:
                im = im.resize((self.w_w, int(height*self.w_w/width)))
                width, height = im.size
            if height>self.w_h:
                im = im.resize((int(width*self.w_h/height),self.w_h ))
                width, height = im.size
            self.photo = ImageTk.PhotoImage(im)
            self.Vcanvas.create_image(0, 0, image = self.photo, anchor = tk.NW)

        self.t.after(self.delay, self.update)


    def previewPic(self,f,outputs):
        self.t = tk.Toplevel(self)
        self.t.geometry('800x600+100+100')
        var0=tk.IntVar()
        self.t.title(f)
        self.t.protocol("WM_DELETE_WINDOW", lambda: var0.set(-1))
        label_0_0 =tk.Label(self.t,text=f,font=("bold",13))
        label_0_0.pack(padx=10,pady=10)
        
        
        self.w_w=640
        self.w_h=480

        canv = tk.Canvas(self.t, width=self.w_w, height=self.w_h, bg='white')
        canv.pack(padx=10,pady=10)

        im = Image.open(f)


        width, height = im.size
        if width>self.w_w:
            im = im.resize((self.w_w, int(height*self.w_w/width)))
            width, height = im.size
        if height>self.w_h:
            im = im.resize((int(width*self.w_h/height),self.w_h ))
            width, height = im.size

        imtk=ImageTk.PhotoImage(im)  # PIL solution


        canv.create_image(0, 0, anchor=tk.NW, image=imtk)
        
        
        butons=[]
        c=0
        for o in outputs:
            name=o.split('/')[-1]
            if len(name)>=10: name=name[:10]+'...'
            butons+=[ttk.Button(self.t, text=name+' ('+str(c+1)+')', command=lambda c=c: var0.set(c))]
            c+=1
            butons[-1].pack(side=tk.LEFT, padx=5, pady=5)
            
        cancelButton = ttk.Button(self.t, text="Quit", command=lambda: var0.set(-1))
        cancelButton.pack(side=tk.RIGHT, padx=5, pady=5)
        
        delButton = ttk.Button(self.t, text="Delete", command =lambda: var0.set(-99))
        delButton.pack(side=tk.RIGHT, padx=5, pady=5)
        
        self.t.wait_variable(var0)
        self.t.destroy()
        
        return var0.get()
        
    def onExit(self):
        self.quit()



def main():
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
    root = tk.Tk()
    root.geometry("800x600+300+300")
    #root.iconbitmap("icono.ico")
    app = Main_app()
    root.mainloop()


if __name__ == '__main__':
    main()

