from tkinter import *

# create window
root = Tk()

# create frames
#topFrame = Frame(root)
#topFrame.pack()

#bottomFrame = Frame(root)
#bottomFrame.pack(side=BOTTOM)

# create buttons
#button1 = Button(topFrame,text="Button 1",fg="red")
#button2 = Button(topFrame,text="Button 2",fg="blue")
#button3 = Button(topFrame,text="Button 3",fg="green")
#button4 = Button(bottomFrame,text="Button 4",fg="black")

# add buttons to frames and pack to left on top frame
#button1.pack(side=LEFT)
#button2.pack(side=LEFT)
#button3.pack(side=LEFT)
#button4.pack(side=TOP)

# create text
#one = Label(root,text="One",bg="black",fg="white")
#two = Label(root,text="Two",bg="black",fg="white")
#three = Label(root,text="Three",bg="black",fg="white")

#one.pack()
#two.pack(fill=X)
#three.pack(side=LEFT,fill=Y)

# layout using grid
l1 = Label(root,text="Name")
l2 = Label(root,text="Password")
entry1 = Entry(root)
entry2 = Entry(root)

l1.grid(row=0)
l2.grid(row=1)

entry1.grid(row=0,column=1)
entry2.grid(row=1,column=1)

# continue from: https://www.youtube.com/watch?v=wNBqM28MMjs

# keep window up until close it
root.mainloop()