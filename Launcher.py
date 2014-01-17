import os
import logo
from LauncherLib import *
from Tkinter import *
from ttk import *

#CONSTANTS

CHECKING_VERSION = 0
DOWNLOADING = 1
UNZIPPING = 2
DONE = 3

API = "https://api.outpostsoftware.com/v1/"
WWW = "http://www.outpostsoftware.com/"
DOWNLOADS = "http://www.outpostsoftware.com/wp-downloads/"

DOWNLOAD_TARGET = ".tmp_download.zip"

TITLE = "Outpost Launcher"

INFO = u"Outpost Launcher \u00A9 Outpost Software"
VERSION = "V0.1"

def get_download_url(version):
    return "".join([DOWNLOADS, "Outpost_", get_platform_name(), "_V", version, ".zip"])

def has_executable():
    out = False
    for file in os.listdir('.'):
        if os.path.splitext(file)[0] == "Outpost":
            out = True
    return out

def has_zip():
    return os.path.exists(DOWNLOAD_TARGET)

class App(Tk):
    def __init__(self):
        Tk.__init__(self)
        self.wm_title(TITLE)
        self.minsize(500, 0)
        self.resizable(False, False)
        self.tk.call('wm', 'iconphoto', self._w, PhotoImage(data=logo.image))
        
        top_frame = Frame(self)
        
        left_frame = Frame(top_frame)
        
        self.message = Label(left_frame)
        self.message.pack(side=TOP, anchor=W)
        
        self.progressbar = Progressbar(left_frame)
        self.progressbar.pack(side=BOTTOM, fill=X)
        
        left_frame.pack(side=LEFT, fill=BOTH, expand=1)
        
        right_frame = Frame(top_frame)
        
        self.play_button = Button(right_frame, text="Play", command=self.play, state=DISABLED)
        self.play_button.pack(fill=BOTH, expand=1)
        
        right_frame.pack(side=RIGHT, fill=BOTH)
        
        top_frame.pack(fill=BOTH, expand=1)
        
        separator = Frame(self, height=2, relief=SUNKEN)
        separator.pack(fill=X, pady=5)
        
        bottom_frame = Frame(self)
        
        info_label = Label(bottom_frame, text=INFO)
        info_label.pack(side=LEFT, anchor=W)
        
        version_label = Label(bottom_frame, text=VERSION)
        version_label.pack(side=RIGHT, anchor=E)
        
        bottom_frame.pack(fill=BOTH, expand=1)
        
        self.reset()
        
        self.after(100, self.update)
    
    def reset(self):
        self.stage = CHECKING_VERSION
        self.message["text"] = "Waiting"
        
        self.progressbar["maximum"] = 1
        self.progressbar["value"] = 0
        
        self.version_request = None
        self.version = None
        self.download_request = None
        self.download_zip = None
    
    def update(self):
        try:
            {CHECKING_VERSION:self.version_update,
             DOWNLOADING:self.download_update,
             UNZIPPING:self.unzip_update,
             DONE:self.done_update}[self.stage]()
        except:
            self.reset()
            raise
        self.after(1, self.update)
    
    def version_update(self):
        if not self.version_request:
            self.version_request = Stream(API + "outpost/version", chunk_size=2**5)
        elif not self.version_request.done:
            self.version_request.update()
        else:
            self.version = parse(self.version_request.result)[0]
            if self.version == read_version():
                if has_executable():
                    self.stage = DONE
                elif has_zip():
                    self.stage = UNZIPPING
                else:
                    self.stage = DOWNLOADING
            else:
                self.stage += 1
    
    def download_update(self):
        if not self.download_request:
            self.download_request = Download(get_download_url(self.version), DOWNLOAD_TARGET)
            self.progressbar["maximum"] = self.download_request.size
            self.message["text"] = "Downloading..."
        elif not self.download_request.done:
            self.download_request.update()
            self.progressbar["value"] = self.download_request.progress
        else:
            self.stage += 1
    
    def unzip_update(self):
        if not self.download_zip:
            self.download_zip = Unzip(DOWNLOAD_TARGET)
            self.progressbar["value"] = 0
            self.progressbar["maximum"] = self.download_zip.size
        elif not self.download_zip.done:
            self.download_zip.update()
            self.progressbar["value"] = self.download_zip.progress
            
            name = self.download_zip.current_file
            if len(name) > 20:
                name = name[:20] + "..."
            self.message["text"] = "Extracting: <" + name + ">"
        else:
            self.stage += 1
            write_version(self.version)
            
    def done_update(self):
        if str(self.play_button["state"]) == str(DISABLED):
            self.play_button["state"] = NORMAL
        self.message["text"] = "Done!"
        self.progressbar["maximum"] = 1
        self.progressbar["value"] = 1
    
    def play(self):
        subprocess.Popen("Outpost")
        self.destroy()

if __name__ == "__main__":
    app = App()
    app.mainloop()