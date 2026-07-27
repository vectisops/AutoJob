import customtkinter as ctk
from typing import List


class ScrollableCheckFrame(ctk.CTkScrollableFrame):
    """Multi-select checklist."""
    def __init__(self, master, items: List[str], **kwargs):
        super().__init__(master, **kwargs)
        self.vars = {}
        for item in items:
            var = ctk.BooleanVar(value=False)
            cb = ctk.CTkCheckBox(self, text=item, variable=var)
            cb.pack(anchor="w", padx=6, pady=2)
            self.vars[item] = var

    def get_selected(self) -> List[str]:
        return [k for k, v in self.vars.items() if v.get()]

    def set_selected(self, selected: List[str]):
        for k, v in self.vars.items():
            v.set(k in selected)


class KeywordListbox(ctk.CTkFrame):
    """Simple add/remove keyword list."""
    def __init__(self, master, title: str = "Keywords", **kwargs):
        super().__init__(master, **kwargs)
        ctk.CTkLabel(self, text=title, font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=4, pady=(4, 0))
        self.entry = ctk.CTkEntry(self, placeholder_text="Add keyword…")
        self.entry.pack(fill="x", padx=4, pady=2)
        self.entry.bind("<Return>", lambda e: self.add())
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=4)
        ctk.CTkButton(btn_frame, text="Add", width=60, command=self.add).pack(side="left", padx=2)
        ctk.CTkButton(btn_frame, text="Remove", width=70, command=self.remove).pack(side="left", padx=2)
        self.listbox = ctk.CTkTextbox(self, height=80)
        self.listbox.pack(fill="both", expand=True, padx=4, pady=4)

    def add(self):
        val = self.entry.get().strip()
        if val:
            current = self.get_keywords()
            if val not in current:
                current.append(val)
                self._set(current)
            self.entry.delete(0, "end")

    def remove(self):
        content = self.listbox.get("1.0", "end").strip().splitlines()
        if content:
            content.pop()
            self._set(content)

    def get_keywords(self) -> List[str]:
        return [l.strip() for l in self.listbox.get("1.0", "end").strip().splitlines() if l.strip()]

    def _set(self, items: List[str]):
        self.listbox.delete("1.0", "end")
        self.listbox.insert("1.0", "\n".join(items))

    def set_keywords(self, items: List[str]):
        self._set(items)
