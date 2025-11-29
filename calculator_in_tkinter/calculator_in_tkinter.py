# Tkinter kutubxonasidan kerakli sinflarni import qilamiz
from tkinter import Tk, Entry, Button, StringVar

# Kalkulyator sinfini yaratamiz
class Calculator:
    def __init__(self, master):
        # Oynaning sarlavhasini o'rnatamiz
        master.title("Calculator")
        # Oynaning o‘lchamini va joylashuvini belgilaymiz (eni x bo‘yi + x joylashuvi + y joylashuvi)
        master.geometry("357x420+0+0")
        # Fon rangini kulrangga (gray) o‘rnatamiz
        master.config(bg="gray")
        # Oynani kattalashtirish yoki kichraytirishni cheklaymiz
        master.resizable(False, False)

        # Ekranda ko‘rsatiladigan matn uchun StringVar() o‘zgaruvchisini yaratamiz
        self.equation = StringVar()
        # Bu yerda foydalanuvchi kiritgan qiymatlar saqlanadi
        self.entry_value = ''
        # Natijani yoki kiritilgan qiymatlarni ko‘rsatish uchun kirish maydonini (Entry) yaratamiz
        Entry(width=16, bg="#ccddff", font=('Areal Bold', 28), textvariable=self.equation).place(x=0, y=0)

        # Har bir tugma (Button) uchun matn, rang, joylashuv va bosilganda bajariladigan amal ko‘rsatilgan
        Button(width=11, height=4, text="(", relief='flat', bg="white", command=lambda: self.show('(')).place(x=0, y=50)
        Button(width=11, height=4, text=")", relief='flat', bg="white", command=lambda: self.show(')')).place(x=90, y=50)
        Button(width=11, height=4, text="%", relief='flat', bg="white", command=lambda: self.show('%')).place(x=180, y=50)
        
        Button(width=11, height=4, text="1", relief='flat', bg="white", command=lambda: self.show(1)).place(x=0, y=125)
        Button(width=11, height=4, text="2", relief='flat', bg="white", command=lambda: self.show(2)).place(x=90, y=125)
        Button(width=11, height=4, text="3", relief='flat', bg="white", command=lambda: self.show(3)).place(x=180, y=125)

        Button(width=11, height=4, text="4", relief='flat', bg="white", command=lambda: self.show(4)).place(x=0, y=200)
        Button(width=11, height=4, text="5", relief='flat', bg="white", command=lambda: self.show(5)).place(x=90, y=200)
        Button(width=11, height=4, text="6", relief='flat', bg="white", command=lambda: self.show(6)).place(x=180, y=200)

        Button(width=11, height=4, text="7", relief='flat', bg="white", command=lambda: self.show(7)).place(x=0, y=275)
        Button(width=11, height=4, text="8", relief='flat', bg="white", command=lambda: self.show(8)).place(x=180, y=275)
        Button(width=11, height=4, text="9", relief='flat', bg="white", command=lambda: self.show(9)).place(x=90, y=275)

        Button(width=11, height=4, text="0", relief='flat', bg="white", command=lambda: self.show(0)).place(x=90, y=350)
        Button(width=11, height=4, text=".", relief='flat', bg="white", command=lambda: self.show('.')).place(x=180, y=350)

        Button(width=11, height=4, text="+", relief='flat', bg="white", command=lambda: self.show('+')).place(x=270, y=275)
        Button(width=11, height=4, text="-", relief='flat', bg="white", command=lambda: self.show('-')).place(x=270, y=200)
        Button(width=11, height=4, text="/", relief='flat', bg="white", command=lambda: self.show('/')).place(x=270, y=50)
        Button(width=11, height=4, text="x", relief='flat', bg="white", command=lambda: self.show('*')).place(x=270, y=125)

        # "=" tugmasi bosilganda hisoblash funksiyasi ishga tushadi
        Button(width=11, height=4, text="=", relief='flat', bg="lightblue", command=self.solve).place(x=270, y=350)
        # "C" tugmasi bosilganda kiritilgan ma’lumotlar o‘chiriladi
        Button(width=11, height=4, text="C", relief='flat', command=self.clear).place(x=0, y=350)


    # show funksiyasi — bosilgan tugma qiymatini ekranga qo‘shadi
    def show(self, value):
        self.entry_value += str(value)   # kiritilgan qiymatni string ko‘rinishida qo‘shamiz
        self.equation.set(self.entry_value)  # Entry oynasida ko‘rsatamiz

    # clear funksiyasi — kiritilgan barcha qiymatlarni tozalaydi
    def clear(self):
        self.entry_value = ''    # qiymatni bo‘shatamiz
        self.equation.set(self.entry_value)  # Entry oynasini tozalaymiz

    # solve funksiyasi — foydalanuvchi kiritgan ifodani hisoblaydi
    def solve(self):
        result = eval(self.entry_value)   # eval() orqali matematik ifodani hisoblaymiz
        self.equation.set(result)         # natijani ekranga chiqaramiz


# Tk oynasini yaratamiz
root = Tk()
# Kalkulyator obyektini yaratamiz va oynaga biriktiramiz
calculator = Calculator(root)
# Tkinter oynasini ishga tushiramiz
root.mainloop()
