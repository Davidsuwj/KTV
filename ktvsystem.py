import os
import tkinter as tk
from tkinter import ttk, messagebox
import vlc  # pip install python-vlc
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL
from ctypes import cast, POINTER
import pygetwindow as gw
import time


class KTVApp:
    def __init__(self, root):
        self.playlist = []
        self.current_song_index = -1
        self.ordered_songs = []
        self.player = vlc.MediaPlayer()

        # Get system volume control
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        self.volume_control = cast(interface, POINTER(IAudioEndpointVolume))

        # UI Components
        root.configure(bg="#222222")

        self.song_list_label = tk.Label(root, text="Wei-Jie KTV娛樂歡唱系統", fg="white", bg="#222222", font=("Grandview", 20, "bold"))
        self.song_list_label.pack(side=tk.TOP, anchor=tk.W, padx=20, pady=20)

        self.song_list_frame = tk.Frame(root)
        self.song_list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=20)

        self.song_list_scrollbar = ttk.Scrollbar(self.song_list_frame)
        self.song_list_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.song_list = ttk.Treeview(self.song_list_frame, yscrollcommand=self.song_list_scrollbar.set,
                                      columns=("Song Name",), show="headings")
        self.song_list.column("Song Name", width=300, stretch=tk.YES)
        self.song_list.heading("Song Name", text="歌曲名稱")
        self.song_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.song_list_scrollbar.configure(command=self.song_list.yview)

        self.controls_frame = tk.Frame(root, bg="#222222")
        self.controls_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=20, pady=20)

        # Search UI
        self.search_entry = tk.Entry(self.controls_frame, width=30)
        self.search_entry.pack(pady=10)
        self.search_button = tk.Button(self.controls_frame, text="搜尋", command=self.search_songs, bg="#4caf50",
                                       fg="white", font=("Arial", 10, "bold"))
        self.search_button.pack(pady=10, fill=tk.X)

        self.volume_scale = tk.Scale(self.controls_frame, from_=0, to=100, orient=tk.HORIZONTAL,
                                     command=self.change_system_volume, bg="#4caf50")
        self.volume_scale.pack(pady=5, fill=tk.X)

        self.ordered_songs_button = tk.Button(self.controls_frame, text="已點歌曲", command=self.show_ordered_songs,
                                              bg="#4caf50", fg="white", font=("Arial", 10, "bold"))
        self.ordered_songs_button.pack(pady=10, fill=tk.X)

        self.play_button = tk.Button(self.controls_frame, text="播放", command=self.play_ordered_songs, bg="#4caf50",
                                     fg="white", font=("Arial", 10, "bold"))
        self.play_button.pack(pady=10, fill=tk.X)

        self.pause_button = tk.Button(self.controls_frame, text="暫停", command=self.pause_song, bg="#f44336",
                                      fg="white", font=("Arial", 10, "bold"))
        self.pause_button.pack(pady=10, fill=tk.X)

        self.next_button = tk.Button(self.controls_frame, text="下一首", command=self.play_next_ordered_song, bg="#f44336",
                                     fg="white", font=("Arial", 10, "bold"))
        self.next_button.pack(pady=10, fill=tk.X)

        self.dianbo_button = tk.Button(self.controls_frame, text="點播", command=self.on_dianbo, bg="#4caf50",
                                       fg="white", state=tk.DISABLED)
        self.dianbo_button.pack(pady=10, fill=tk.X)

        self.chabo_button = tk.Button(self.controls_frame, text="插播", command=self.on_chabo, bg="#4caf50",
                                      fg="white", state=tk.DISABLED)
        self.chabo_button.pack(pady=10, fill=tk.X)

        self.stop_button = tk.Button(self.controls_frame, text="關閉影音", command=self.stop_song, bg="#f44336",
                                     fg="white", font=("Arial", 10, "bold"))
        self.stop_button.pack(pady=10, fill=tk.X)

        # Load songs
        self.load_songs("E:\\all mv")

        # Song info frame
        self.song_info_frame = tk.Frame(self.controls_frame, bg="#222222")
        self.song_info_frame.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Bind event to song list
        self.song_list.bind("<Button-1>", self.on_song_selected)

        # Set button backgrounds to transparent
        self.search_button.configure(highlightbackground=root.cget("bg"))
        self.play_button.configure(highlightbackground=root.cget("bg"))
        self.pause_button.configure(highlightbackground=root.cget("bg"))
        self.next_button.configure(highlightbackground=root.cget("bg"))
        self.dianbo_button.configure(highlightbackground=root.cget("bg"))
        self.chabo_button.configure(highlightbackground=root.cget("bg"))
        self.stop_button.configure(highlightbackground=root.cget("bg"))

    def load_songs(self, directory):
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith(".mp4"):
                    self.playlist.append(os.path.join(root, file))
                    song_name = file.replace(".mp4", "")  # Remove the file extension
                    self.song_list.insert("", tk.END, values=(song_name,))

    def on_song_selected(self, event):
        item = self.song_list.identify("item", event.x, event.y)
        song_name = self.song_list.item(item, "values")[0]
        song_path = os.path.join("E:\\all mv", song_name + ".mp4")  # Construct the full path

        # Enable the point and insert buttons
        self.dianbo_button.config(state=tk.NORMAL)
        self.chabo_button.config(state=tk.NORMAL)

        # Remove previous song info frame
        self.song_info_frame.destroy()

        # Show the selected song on the right side of the song list
        self.song_info_frame = tk.Frame(self.controls_frame, bg="#222222")
        self.song_info_frame.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.BOTH, expand=True)

    def play_ordered_songs(self):
        if self.ordered_songs:
            self.current_song_index = self.playlist.index(self.ordered_songs[0])
            self.play_song()

    def play_next_ordered_song(self):
        if self.ordered_songs:
            self.ordered_songs.pop(0)  # Remove the current song from the ordered_songs list
            if self.ordered_songs:
                self.current_song_index = self.playlist.index(self.ordered_songs[0])
                self.play_song()

    def play_song(self):
        

        if self.current_song_index > -1:
          self.player.set_media(vlc.Media(self.playlist[self.current_song_index]))
          self.player.play()
          self.player.video_set_scale(0)
          time.sleep(0.5)

        vlc_window = None
        while not vlc_window:
            time.sleep(1)
            for window in gw.getAllWindows():
                if 'VLC' in window.title:
                    vlc_window = window
                    break

        # Move VLC window to the specified position (second display)
        vlc_window.moveTo(1920, 0)
        time.sleep(0.5)
        self.player.toggle_fullscreen()
        time.sleep(1)  # Adjust the delay time here if needed
        vlc_window.moveTo(1920, 0)
       
        # Ensure the window is fully in focus for the fullscreen toggle
        vlc_window.activate()
        time.sleep(0.1)

        # Move VLC window to the specified position again (in case it shifted during fullscreen)
        

    def pause_song(self):
        self.player.pause()

    def stop_song(self):
        self.player.stop()

    def change_system_volume(self, volume_level):
        volume = int(volume_level) / 100.0
        self.volume_control.SetMasterVolumeLevelScalar(volume, None)

    def search_songs(self):
        query = self.search_entry.get().lower()
        matching_songs = [song_path for song_path in self.playlist if query in os.path.basename(song_path).lower()]
        self.show_search_results(matching_songs)

    def show_search_results(self, songs):
        # Clear the song list
        self.song_list.delete(*self.song_list.get_children())

        # Display the search results in the song list
        for song_path in songs:
            song_name = os.path.basename(song_path).replace(".mp4", "")
            self.song_list.insert("", tk.END, values=(song_name,))

    def show_ordered_songs(self):
        ordered_songs_window = tk.Toplevel(self.song_list.master)
        ordered_songs_window.title("已點歌曲")
        ordered_songs_window.geometry("400x300")

        ordered_songs_list = tk.Listbox(ordered_songs_window)
        for song in self.ordered_songs:
            ordered_songs_list.insert(tk.END, os.path.basename(song))
        ordered_songs_list.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        def start_playback():
            if self.ordered_songs:
                self.current_song_index = self.playlist.index(self.ordered_songs[0])
                self.play_song()

        start_button = tk.Button(ordered_songs_window, text="開始", command=start_playback, bg="#4caf50", fg="white")
        start_button.pack(side=tk.LEFT, padx=10, pady=10)

        def delete_song():
            selected_song = ordered_songs_list.curselection()
            if selected_song:
                index = selected_song[0]
                deleted_song = self.ordered_songs.pop(index)
                ordered_songs_list.delete(selected_song)
                messagebox.showinfo("資訊", f"已刪除歌曲 {os.path.basename(deleted_song)}")

        delete_button = tk.Button(ordered_songs_window, text="刪除", command=delete_song, bg="#f44336", fg="white")
        delete_button.pack(side=tk.LEFT, padx=10, pady=10)

        def go_back():
            ordered_songs_window.destroy()

        back_button = tk.Button(ordered_songs_window, text="返回", command=go_back, bg="#f44336", fg="white")
        back_button.pack(side=tk.LEFT, padx=10, pady=10)

        # Add pause, stop, and next buttons to the ordered_songs_window
        pause_button = tk.Button(ordered_songs_window, text="暫停", command=self.pause_song, bg="#f44336", fg="white")
        pause_button.pack(side=tk.LEFT, padx=10, pady=10)

        next_button = tk.Button(ordered_songs_window, text="下一首", command=self.play_next_ordered_song, bg="#4caf50", fg="white")
        next_button.pack(side=tk.LEFT, padx=10, pady=10)

        # Add volume scale to the ordered_songs_window
        volume_scale = tk.Scale(ordered_songs_window, from_=0, to=100, orient=tk.HORIZONTAL,
                                command=self.change_system_volume, bg="#4caf50")
        volume_scale.pack(pady=5)

    def on_dianbo(self):
        item = self.song_list.selection()[0]
        song_name = self.song_list.item(item, "values")[0]
        song_path = os.path.join("E:\\all mv", song_name + ".mp4")  # Construct the full path

        # Append the selected song to the end of ordered_songs
        self.ordered_songs.append(song_path)  # Add the full path to ordered_songs
        messagebox.showinfo("資訊", f"歌曲 {song_name} 已點播")

        # Disable the point and insert buttons
        self.dianbo_button.config(state=tk.DISABLED)
        self.chabo_button.config(state=tk.DISABLED)

    def on_chabo(self):
        item = self.song_list.selection()[0]
        song_name = self.song_list.item(item, "values")[0]
        song_path = os.path.join("E:\\all mv", song_name + ".mp4")  # Construct the full path

        # Insert the selected song to the beginning of ordered_songs
        self.ordered_songs.insert(1, song_path)  # Add the full path to ordered_songs
        messagebox.showinfo("資訊", f"歌曲 {song_name} 已插播")

        # Disable the point and insert buttons
        self.dianbo_button.config(state=tk.DISABLED)
        self.chabo_button.config(state=tk.DISABLED)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("KTV App")
    root.geometry("900x600")

    app = KTVApp(root)

    # Set the font size and weight of the song list
    style = ttk.Style()
    style.configure("Treeview", font=("Arial", 14, "bold"))

    root.mainloop()