import customtkinter as ctk
from tkinter import messagebox
import sqlite3

# --- APPEARANCE SETTINGS ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class MovieApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Movie Watchlist Pro v1.2")
        self.geometry("650x850")

        self.init_db()
        self.create_widgets()
        self.refresh_list()

    def init_db(self):
        conn = sqlite3.connect("movies.db")
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS movies 
                          (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                           title TEXT NOT NULL, 
                           genre TEXT, 
                           status TEXT)''')
        conn.commit()
        conn.close()

    def create_widgets(self):
        # Header
        self.label = ctk.CTkLabel(self, text="🎬 My Watchlist", font=("Helvetica", 24, "bold"))
        self.label.pack(pady=20)

        # --- ADD MOVIE PANEL ---
        self.input_frame = ctk.CTkFrame(self)
        self.input_frame.pack(pady=10, padx=20, fill="x")

        self.entry_title = ctk.CTkEntry(self.input_frame, placeholder_text="Movie Title...", width=200)
        self.entry_title.grid(row=0, column=0, padx=10, pady=10)

        self.entry_genre = ctk.CTkEntry(self.input_frame, placeholder_text="Genre...", width=200)
        self.entry_genre.grid(row=0, column=1, padx=10, pady=10)

        self.add_button = ctk.CTkButton(self.input_frame, text="Add", command=self.add_movie, width=100)
        self.add_button.grid(row=0, column=2, padx=10, pady=10)

        # --- SEARCH PANEL ---
        self.search_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.search_frame.pack(pady=10, padx=20, fill="x")
        
        # We use .bind() to trigger search on every key release
        self.search_entry = ctk.CTkEntry(self.search_frame, placeholder_text="🔍 Search in your list...", width=580)
        self.search_entry.pack(padx=10, pady=5)
        self.search_entry.bind("<KeyRelease>", lambda event: self.refresh_list())

        # List Panel
        self.list_label = ctk.CTkLabel(self, text="Your Collection:", font=("Helvetica", 14, "italic"))
        self.list_label.pack(pady=(10, 0))

        self.scrollable_frame = ctk.CTkScrollableFrame(self, width=600, height=450)
        self.scrollable_frame.pack(pady=10, padx=20, fill="both", expand=True)

    def add_movie(self):
        title = self.entry_title.get()
        genre = self.entry_genre.get()
        if title.strip() == "":
            messagebox.showwarning("Warning", "Please enter a title!")
            return

        conn = sqlite3.connect("movies.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO movies (title, genre, status) VALUES (?, ?, ?)", (title, genre, "Pending"))
        conn.commit()
        conn.close()

        self.entry_title.delete(0, 'end')
        self.entry_genre.delete(0, 'end')
        self.refresh_list()

    def toggle_status(self, movie_id, current_status):
        new_status = "Watched" if current_status == "Pending" else "Pending"
        conn = sqlite3.connect("movies.db")
        cursor = conn.cursor()
        cursor.execute("UPDATE movies SET status = ? WHERE id = ?", (new_status, movie_id))
        conn.commit()
        conn.close()
        self.refresh_list()

    def delete_movie(self, movie_id):
        conn = sqlite3.connect("movies.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM movies WHERE id = ?", (movie_id,))
        conn.commit()
        conn.close()
        self.refresh_list()

    def refresh_list(self):
        """Refreshes the list, applying search filter if any."""
        search_query = self.search_entry.get().lower()

        # Clear existing widgets
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        conn = sqlite3.connect("movies.db")
        cursor = conn.cursor()
        
        # Use SQL LIKE for efficient searching directly in DB
        cursor.execute("SELECT * FROM movies WHERE LOWER(title) LIKE ? OR LOWER(genre) LIKE ? ORDER BY id DESC", 
                       (f'%{search_query}%', f'%{search_query}%'))
        movies = cursor.fetchall()
        conn.close()

        for movie in movies:
            m_id, m_title, m_genre, m_status = movie
            
            row = ctk.CTkFrame(self.scrollable_frame)
            row.pack(fill="x", pady=5, padx=5)

            text_color = "#2ecc71" if m_status == "Watched" else "white"
            status_emoji = "✅ " if m_status == "Watched" else "⏳ "

            lbl = ctk.CTkLabel(row, text=f"{status_emoji} {m_title} ({m_genre})", 
                               font=("Helvetica", 13), text_color=text_color)
            lbl.pack(side="left", padx=10)

            btn_del = ctk.CTkButton(row, text="Delete", fg_color="#cc3300", hover_color="#990000", 
                                    width=60, height=24, command=lambda i=m_id: self.delete_movie(i))
            btn_del.pack(side="right", padx=10, pady=5)

            btn_text = "Undo" if m_status == "Watched" else "Watched"
            btn_color = "#3498db" if m_status == "Watched" else "#27ae60"

            btn_status = ctk.CTkButton(row, text=btn_text, fg_color=btn_color,
                                       width=80, height=24, 
                                       command=lambda i=m_id, s=m_status: self.toggle_status(i, s))
            btn_status.pack(side="right", padx=5)

if __name__ == "__main__":
    app = MovieApp()
    app.mainloop()