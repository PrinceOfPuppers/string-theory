import tkinter as tk
import numpy as np
import matplotlib.pyplot as plt

from helperFuncs import getTuningList,getPlotSize,makeLabel,makeGraphText



#wrappers for app methods
def keyUpFifth(cfg,app,ax):
    if cfg.debug:
        print("Key Change: Up a Fifth")
    app.keyChange(5)

    newTitle,stringLabels,fretLabels=makeGraphText(app)

    showIntervalArray(app,cfg,ax,newTitle,stringLabels,fretLabels)

def keyDownFourth(cfg,app,ax):
    if cfg.debug:
        print("Key Change; Down a Fourth")
    app.keyChange(4)

    newTitle,stringLabels,fretLabels=makeGraphText(app)

    showIntervalArray(app,cfg,ax,newTitle,stringLabels,fretLabels)

def changeModeToClicked(cfg,app,ax,boxClicked):
    newRootInterval=app.intervalArray[boxClicked[0]][boxClicked[1]]
    if newRootInterval!=app.nonIntervalNum:
        if cfg.debug:
            print("Setting {} as new root".format(int(newRootInterval)))
        app.changeMode(newRootInterval)

        newTitle,stringLabels,fretLabels=makeGraphText(app)

        showIntervalArray(app,cfg,ax,newTitle,stringLabels,fretLabels)

#wrapper for updating plot
def showIntervalArray(app,cfg,ax,title,stringLabels,fretLabels):
    ax.clear()
    
    ax.imshow(app.intervalArray,cmap=cfg.colorMap)
    ax.set_xticks(np.arange(len(fretLabels)))
    ax.set_yticks(np.arange(len(stringLabels)))
    
    for i in range(len(stringLabels)):  
        for j in range(len(fretLabels)):
            interval=int(app.intervalArray[i, j])
            label=makeLabel(app,cfg,interval)
            ax.text(j, i, label, ha="center", va="center", color="black")

    plt.title(title,color='white')
    
    ax.set_xticklabels(fretLabels,color='white')
    ax.set_yticklabels(stringLabels,color='white')
    
    plt.gca().invert_yaxis()

    plt.show()



#generates new plot window, used when generate button is hit in tkinter window
def generateAndShowPlot(app,cfg,tuning,root,scale):
    app.update(scale,root,tuning)
    app.makeIntervalArray()
    title,stringLabels,fretLabels=makeGraphText(app)

    
    plt.close()

    fig=plt.figure(figsize=getPlotSize(fretLabels,stringLabels),num="Click To Change Root, Scroll To Change Key")
    ax=fig.add_subplot(111)
    fig.patch.set_facecolor('#404040')

    #bootstraps event handler
    eventHand=EventHandler()
    eventHand.enableInteractivity(cfg,app,ax,fig)

    plt.tight_layout()
    showIntervalArray(app,cfg,ax,title,stringLabels,fretLabels)

class EventHandler:
    def __init__(self):
        pass
    
    def enableInteractivity(self,cfg,app,ax,fig):
        self.scrolling=fig.canvas.mpl_connect('scroll_event',lambda event: self.onScroll(event,cfg,app,ax,fig))
        self.clicking=fig.canvas.mpl_connect('button_press_event', lambda event: self.onClick(event,cfg,app,ax,fig))

    def disableInteractivity(self,fig):
        fig.canvas.mpl_disconnect(self.scrolling)
        fig.canvas.mpl_disconnect(self.clicking)

    #callback fucntions 
    def onScroll(self,event,cfg,app,ax,fig):
        if event.button=="up":
            keyUpFifth(cfg,app,ax)
        if event.button=="down":
            keyDownFourth(cfg,app,ax)

    def onClick(self,event,cfg,app,ax,fig):
        if cfg.debug:
            print("clicked on",event.xdata,event.ydata)

        if event.button == cfg.mouseButton:
            #input may be none type
            if type(event.ydata)!=np.float64 or type(event.xdata)!=np.float64:
                if cfg.debug:
                    print("clicked offscreen")
            else:
                #coordinates are flipped
                boxClicked=(int(event.ydata+0.5),int(event.xdata+0.5))

                changeModeToClicked(cfg,app,ax,boxClicked)


class Gui:
    def __init__(self,app,cfg,tkRoot):
        self.generateTkinterObjs(app,cfg,tkRoot)
        self.makeLayout()

    def generateTkinterObjs(self,app,cfg,tkRoot):
        tkRoot.geometry(cfg.tkinterWinSize)
        tkRoot.option_add( "*font", cfg.tkinterFont)
        window=tk.Frame(tkRoot)
        window.pack(fill='both',expand=True)
        window.configure(background= '#404040')


        #root note selection
        rootLabel=tk.Label(window,text="Root:")
        rootLabel.configure(background= '#404040',foreground="white",borderwidth=2)
        root = tk.StringVar(window)
        root.set(app.noteList[0])

        rootDropDown = tk.OptionMenu(window, root, *app.noteList)
        rootDropDown.configure(background= '#808080',highlightthickness=0)
        rootDropDown["menu"].configure(background= '#808080')


        #scale selection
        scaleLabel=tk.Label(window,text="Scale:")
        scaleLabel.configure(background= '#404040',foreground="white")

        scale = tk.StringVar(window)
        scale.set(app.diatonicList[0])

        scaleDropDown = tk.OptionMenu(window, scale, *app.diatonicList)
        scaleDropDown.configure(background= '#808080',highlightthickness=0)
        scaleDropDown["menu"].configure(background= '#808080')

        #tuning
        tuningLabel=tk.Label(window,text="Tuning:")
        tuningLabel.configure(background= '#404040',foreground="white")

        tuningStrVar=tk.StringVar(window)
        tuningStrVar.set(cfg.defaultTuning)
        tuningTextBox=tk.Entry(window,textvariable=tuningStrVar, justify="center")
        tuningTextBox.configure(background= '#808080',highlightthickness=0)


        #generate button
        generateButton=tk.Button(window,text="Generate",command=lambda: generateAndShowPlot(app,cfg,getTuningList(tuningStrVar),root.get(),scale.get()))
        generateButton.configure(background= 'red',activebackground='#404040')

    
        self.window=window
        self.rootLabel=rootLabel
        self.rootDropDown=rootDropDown
        self.scaleLabel=scaleLabel
        self.scaleDropDown=scaleDropDown
        self.tuningLabel=tuningLabel
        self.tuningTextBox=tuningTextBox
        self.generateButton=generateButton
    
    def makeLayout(self):
        self.rootLabel.grid(row=0,column=0)
        self.rootDropDown.grid(row=0,column=1,sticky=tk.NSEW)

        self.scaleLabel.grid(row=1,column=0)
        self.scaleDropDown.grid(row=1,column=1,sticky=tk.NSEW)

        self.tuningLabel.grid(row=2,column=0,sticky=tk.NSEW)
        self.tuningTextBox.grid(row=2,column=1,sticky=tk.NSEW)

        self.generateButton.grid(row=3, columnspan=2,sticky=tk.NSEW)


        for row in range(0,4):
            for column in range(0,2):
                self.window.columnconfigure(column, weight=1)
                self.window.rowconfigure(row,weight=1)
    
    def mainLoop(self,tkRoot):
        tkRoot.mainloop()