
#all modules and widgets used
import Tkinter as tk
from PIL import Image, ImageTk
import copy
import random
import tkFileDialog
import tkMessageBox
import tkFont
import tkSimpleDialog

#########Prokudin-Groskii's Negatives##########################

############I have the negatives!##########################

def wrapperAlignNegatives():
    #function serves as a wrapper for alignNegatives

    try:
        
        #gets the filename and directory where to save
        file = gorskiicanvas.data.filename
        saveFolder = gorskiicanvas.data.foldername
        
        if(isValidFilename(file)):
            
            image = Image.open(file)
            colored = alignNegatives(image)
            colored.show()

            #saves file
            fn = tuple(file.split('.'))
            colored.save("%s/Negative-aligned.jpg"%(saveFolder))

            #tells user when done saving
            message = "Edited image has been saved! You may exit browser!"
            title = "Finished!"
            tkMessageBox.showinfo(title, message)
            
        else: #invalid file type
            
            message = "You entered an invalid file type!"
            title = "Invalid file"
            tkMessageBox.showerror(title, message)

    except: #no filename or directory

        message = "Oops! You forgot to choose a file or save folder!"
        title = "Missing file or save folder"
        tkMessageBox.showerror(title, message)
        

def alignNegatives(image):
    #aligns the negatives (r,g,b) plates

    #checks to make sure image is greyscale before aligning
    if(checkGreyscale(image)):
        
        blue, green, red = splitImage(image)
        size = red.size
        red, green, blue = pyramid(red, green, blue, 100)
        colImage = coloredImage(red, blue, green, size)
        
        return colImage

def isValidFilename(file):
    #checks if file is valid

    #makes sure that file has a . in it
    #(must have a tag (ex: .png, .jpg, etc)
    if(file.find('.') == -1):
        return False

    #acceptable file types
    filetypes = set(['jpg', 'png','gif'])
    a = file.split('.')

    #checks to see that file is acceptable type
    if a[-1] not in filetypes:
        return False

    return True

def checkGreyscale(image):
    #checks if image is grayscale 
    
    pixel = image.load()
    (width, height) = image.size
    
    for x in xrange(width):
        for y in xrange(height):
            
            #if is L for all x,y, automatically returns True
            if(not checkL(image)):
                if(len(pixel[x,y]) == 4): #RGBA
                    red,green,blue,alpha = pixel[x,y]
                    
                else: #RGB
                    red,green,blue = pixel[x,y]

                #if r,g,b values are equal for all x,y, returns True
                if((red != green) or (green != blue) or (blue != red)):
                    return False
                
    return True

def splitImage(image):
    #crops the photo into three images to align for gorskii photos
    
    pixel = image.load()
    (width, height) = image.size
    smallHeight = height/3

    #separates image by top,middle,bottom (vertically)
    topImage = image.crop((0,0,width,smallHeight))
    middleImage = image.crop((0,smallHeight,width,smallHeight*2))
    bottomImage = image.crop((0,smallHeight*2,width,smallHeight*3))
    
    return topImage, middleImage, bottomImage

def pyramid(r, g, b, maxwidth):
    #faster way of checking where align smaller images and use those
    #coordinates to minimize time in aligning big image
    
    (width, height) = r.size
    
    #contains list of images of the resized r,g,b
    reds = [r] 
    greens = [g]
    blues = [b]

    #lists contain images that are half the size of the previous
    while(width > maxwidth):
        reds.append(r.resize((width/2, height/2)))
        greens.append(g.resize((width/2, height/2)))
        blues.append(b.resize((width/2, height/2)))
        width /= 2
        height /= 2

    #reverses lists so that images go from small to large
    reds.reverse()
    greens.reverse()
    blues.reverse()

    #goes through list from small to large
    for i in xrange(len(reds)):
        #offset coordinates based on blue plate
        dxBG, dyBG = findminimumDiff(blues[i], greens[i])
        dxBR, dyBR = findminimumDiff(blues[i], reds[i])
        for j in xrange(i, len(reds)):
            #moves the larger images accordingly
            greens[j] = moveImage(greens[j], dxBG, dyBG)
            reds[j] = moveImage(reds[j], dxBR, dyBR)
            dxBG *= 2
            dyBG *= 2
            dxBR *= 2
            dyBR *= 2
            
    return (reds[-1], greens[-1], blues[-1])
                                #returns largest sized image
    
def findDifference(image1, image2, (dx, dy), border):
    #find the difference between two images (thus finding how different
    #the two images are)
    
    (width, height) = image1.size
    image1 = image1.load()
    image2 = image2.load()

    #calculates the 'moved' image pixels if out of bounds,
    #wraps around
    summation = 0
    
    for i in xrange(border, width-border):
        for j in xrange(border, height-border):
            x = (i + dx) % width
            y = (j + dy) % height
            difference = image1[i,j] - image2[x, y]
            
            #checks to see the difference between the two images
            summation += difference**2
            
    return summation

def moveImage(image, dx, dy):
    #moves image by (dx,dy)
    
    width, height = image.size
    iPixels = image.load()
    rImage = Image.new('L', image.size)
    rPixels = rImage.load()

    #moves image with pixels and wraps around when out of bounds
    for i in xrange(width):
        for j in xrange (height):
            x = (i + dx) % width
            y = (j + dy) % height
            rPixels[i, j] = iPixels[x, y]
            
    return rImage

def findminimumDiff(image1, image2, n=3):
    #finds the minimum difference of the two images
    
    mini = 1e9999 # need a big value here
    border = image1.size[0]/10 # border that doesn't get checked

    #sum of differences with the move represented in (dx,dy)
    sumsOfDiffs = [] #[(dx, dy), value]
    for dx in xrange(-n, n+1):
        for dy in xrange(-n, n+1):
            value = findDifference(image1, image2, (dx, dy), border)
            sumsOfDiffs.append(((dx, dy), value))
            
    # returns min transform(dx,dy) based on differences (second value)
    return min(sumsOfDiffs, key=lambda i: i[1])[0]

def coloredImage(red, blue, green, size, alpha=100):
    #puts the plates together to create a colored image
    
    #returns colored RGBA image of same size as input
    colorImage = Image.new('RGBA', size)
    pixels = colorImage.load()
    (width, height) = size

    #contains r,b,g pixel values respectively
    rPixels = red.load()
    bPixels = blue.load()
    gPixels = green.load()

    #assigns pixel values (r,g,b,a)
    for x in xrange(width):
        for y in xrange(height):
            pixels[x,y] = (rPixels[x,y],gPixels[x,y],bPixels[x,y],alpha)
            
    return colorImage



#########Create Negatives from input!##########################


def negative(image):
    #creates a negative of the colored image in strip imitating
    #gorskii negatives
    
    #assumes that image is RBG or RBGA image
    pixels = image.load()
    width, height = image.size
    rValues = Image.new('L',image.size)
    gValues = Image.new('L',image.size)
    bValues = Image.new('L',image.size)
    
    #assigns red, green, blue values in separate greyscale images
    rPixels,gPixels,bPixels = rValues.load(),gValues.load(),bValues.load()
    
    for x in xrange(width):
        for y in xrange(height):
            if(len(pixels[x,y]) == 4):
                rPixels[x,y],gPixels[x,y],bPixels[x,y],a = pixels[x,y]
            else:
                rPixels[x,y],gPixels[x,y],bPixels[x,y] = pixels[x,y]

    #list in order BGR
    listOfRGB = [bValues,gValues,rValues]
    
    return listOfRGB

def wrapperNegative():
    #wrapper for negative function

    try:
        #finds file and the directory where image is to be saved
        file = gorskiicanvas.data.filename
        saveFolder = gorskiicanvas.data.foldername

        if(isValidFilename(file)):
            image = Image.open(file)
            listOfRGB = negative(image)
            
            #assembles the strip so that blues go on top,
            #greens middle, reds bottom
            strip = assemble(listOfRGB,3,1,20)

            #saves image in saveFolder
            strip.show()
            fn = tuple(file.split('.'))
            strip.save("%s/Image-negative.%s"%(saveFolder,fn[-1]))

            #tells user when done saving
            message = "Edited image has been saved! You may exit browser!"
            title = "Finished!"
            tkMessageBox.showinfo(title, message)
            
        else: #if invalid file
            
            message = "You entered an invalid file type!"
            title = "Invalid file"
            tkMessageBox.showerror(title, message)

    except: #no filename or directory

        message = "Oops! You forgot to choose a file or save folder!"
        title = "Missing file or save folder"
        tkMessageBox.showerror(title, message)

def assemble(listOfIm,rows,cols,border=0):
    #puts together a list of images by how many rows and cols wanted
    
    standardSize = listOfIm[0].size
    
    #checks to see that all images in list are same size
    for element in listOfIm:
        if(element.size != standardSize):
            print "Cannot assemble image of different sizes!"
            return listOfIm
        
    sWidth,sHeight = standardSize
    nWidth,nHeight = ((sWidth*cols)+(border*(cols+1)),
                      (sHeight*rows)+(border*(rows+1)))
    
    #returns the value of the original image
    #(if L returns L, if RGB or RGBA, returns RGB or RGBA
    if(checkL(listOfIm[0])):
        newImage = Image.new('L', (nWidth,nHeight))
    else:
        newImage = Image.new('RGBA', (nWidth,nHeight))

    nPixels = newImage.load()
    count = 0
    
    #goes through each image in list
    for row in xrange(rows):
        for col in xrange(cols):
            image = listOfIm[count]
            iPixels = image.load()

            #copies the pixels of the image into the given row,col
            for x in xrange(sWidth):
                for y in xrange(sHeight):
                    newX = ((sWidth*col)+x)+(border*(col+1))
                    newY = ((sHeight*row)+y)+(border*(row+1))
                    
                    #check to see if image is 'L' greyscale image
                    if(checkL(image)):
                        nPixels[newX,newY] = iPixels[x,y]
                    #check to see if image is 'RGB' image (3 values)
                    elif(len(iPixels[x,y]) == 3):
                        r,g,b = iPixels[x,y]
                        nPixels[newX,newY] = (r,g,b, 100)
                    else: #RGBA image
                        nPixels[newX,newY] = iPixels[x,y]
            count +=1
            
    return newImage
    

#########Create Negatives and realign!##########################

def wrapperMakeShiftedStrip():
    #makes a strip and then aligns it given random shifts

    try:
        #find file and directory to be saved into
        file = gorskiicanvas.data.filename
        saveFolder = gorskiicanvas.data.foldername
                       
        if(isValidFilename(file)):

            image = Image.open(file)
            listOfRGB = negative(image)
            (width, height) = image.size

            #shifts,assemble,realign images
            #borders 2% of width
            border = .02*width
            shiftedList = randomshift(listOfRGB,int(border))
            strip = assemble(shiftedList,3,1)
            realigned = alignNegatives(strip)

            #save to saveFolder
            realigned.show()
            fn = tuple(file.split('.'))
            realigned.save("%s/Image-realigned.%s"%(saveFolder,fn[-1]))

            #tells user when done saving
            message = "Edited image has been saved! You may exit browser!"
            title = "Finished!"
            tkMessageBox.showinfo(title, message)
            
        else: #if not valid file

            message = "You entered an invalid file type!"
            title = "Invalid file"
            tkMessageBox.showerror(title, message)

    except: #no filename or directory

        message = "Oops! You forgot to choose a file or save folder!"
        title = "Missing file or save folder"
        tkMessageBox.showerror(title, message)

def randomshift(listOfRGB,border):
    #randomly shifts the images so that when aligned, there will be
    #some noise on the borders
    
    sWidth,sHeight = listOfRGB[0].size

    #randomly shifts each image
    newShiftedImages = []
    for element in listOfRGB:
        
        #shifts 2% of width and height
        shiftAmountX = int(sWidth*.02)
        shiftAmountY = int(sHeight*.02)

        #generates random shifts x and y with randint
        dx = random.randint(-shiftAmountX,shiftAmountX)
        dy = random.randint(-shiftAmountY,shiftAmountY)
        
        shiftedImage = moveImage(element, dx, dy)
        newShiftedImages.append(shiftedImage)
    
    #gives a border to each image
    newBorderedImages = []
    for image in newShiftedImages:
        newBordered = Image.new('L', (sWidth+border*2,sHeight+border*2))
        nPixels = newBordered.load()
        iPixels = image.load()
        for x in xrange(sWidth):
            for y in xrange(sHeight):
                nPixels[border+x,border+y] = iPixels[x,y]
        newBorderedImages.append(newBordered)

    return newBorderedImages


############################Greyscale##########################

def wrapperGreyscale():
    #acts as a wrapper for greyscale function

    try:
        #file and directory to be saved to
        file = filtercanvas.data.filename
        saveFolder = filtercanvas.data.foldername
        
        if(isValidFilename(file)):
            
            image = Image.open(file)
            returnImage = greyscale(image)

            #image saved to saveFolder
            returnImage.show()
            fn = tuple(file.split('.'))
            returnImage.save("%s/Image-grey.%s"%(saveFolder,fn[-1]))
            
            #tells user when done saving
            message = "Edited image has been saved! You may exit browser!"
            title = "Finished!"
            tkMessageBox.showinfo(title, message)

        else: #if file not valid

            message = "You entered an invalid file type!"
            title = "Invalid file"
            tkMessageBox.showerror(title, message)

    except: #no filename or directory

        message = "Oops! You forgot to choose a file or save folder!"
        title = "Missing file or save folder"
        tkMessageBox.showerror(title, message)

def greyscale(image):
    #greyscales image

    #check what type of image it is
    pixels = image.load()
    if(type(pixels[0,0]) == int): #L
        returnImage = Image.new('L', image.size)
    else: #color so defaults to RGBA
        returnImage = Image.new('RGBA', image.size)
        
    rPixels = returnImage.load()
    width, height = image.size
    
    for x in xrange(width):
        for y in xrange(height):

            #checks to see if RGB or RGBA
            if(len(pixels[x,y]) == 4): #RGBA
                red, green, blue, alpha = pixels[x,y]
            else: #RGB
                red, green, blue = pixels[x,y]
                alpha = 100

            #luminosity algorithm that mirrors human eye values
            oRed = .21*red
            oGreen = .71*green
            oBlue = .07*blue
            
            average = int(oRed + oGreen + oBlue)
            
            if(type(rPixels[x,y]) == int): #L
                rPixels[x,y] = average
            else: #RGBA
                rPixels[x,y] = (average,average,average,100)
            
    return returnImage

############################Sepia##########################

def wrapperSepia():
    #acts as wrapper for sepia function

    try:
        #find file and directory to save to
        file = filtercanvas.data.filename
        saveFolder = filtercanvas.data.foldername
        
        if(isValidFilename(file)):
            
            image = Image.open(file)
            returnImage = sepia(image)

            #save to saveFolder
            returnImage.show()
            fn = tuple(file.split('.'))
            returnImage.save("%s/Image-sepia.%s"%(saveFolder,fn[-1]))

            #tells user when done saving
            message = "Edited image has been saved! You may exit browser!"
            title = "Finished!"
            tkMessageBox.showinfo(title, message)

        else: #if not valid file

            message = "You entered an invalid file type!"
            title = "Invalid file"
            tkMessageBox.showerror(title, message)

    except: #no filename or directory

        message = "Oops! You forgot to choose a file or save folder!"
        title = "Missing file or save folder"
        tkMessageBox.showerror(title, message)
    

def sepia(image):
    #sepias image
    
    if(not(checkGreyscale(image))): #check to see if greyscale already
        image = greyscale(image)

    image = contrast(image) #makes lights and darks more clear for filter
    returnImage = Image.new('RGBA', image.size)
    
    rPixels = returnImage.load()
    pixels = image.load()
    width, height = image.size

    #sepia color values
    sRed = 94*2.5
    sGreen = 38*2.5
    sBlue = 18*2.5
    
    for x in xrange(width):
        for y in xrange(height):

            grey = pixels[x,y]

            if(type(grey) != int):
                grey = grey[0] #since already greyscale all values are the same
            
            #sepia: red, green, blue ratios (found online)
            oRed = grey*((sRed*.393) + (sGreen*.769) + (sBlue*.189))/255
            oGreen = grey*((sRed*.349) + (sGreen*.686) + (sBlue*.168))/255
            oBlue = grey*((sRed*.272) + (sGreen*.534) + (sBlue*.131))/255
            
            rPixels[x,y] = (int(oRed), int(oGreen), int(oBlue), 100)
            
    return returnImage

############################Contrast##########################

def wrapperContrast():
    #wrapper for contrast function

    try:
        #file and directory to save to
        file = filtercanvas.data.filename
        saveFolder = filtercanvas.data.foldername
        
        if(isValidFilename(file)):
            
            image = Image.open(file)
            returnImage = contrast(image)

            #save to saveFolder
            returnImage.show()
            fn = tuple(file.split('.'))
            returnImage.save("%s/Image-contrast.%s"%(saveFolder,fn[-1]))
            
            #tells user when done saving
            message = "Edited image has been saved! You may exit browser!"
            title = "Finished!"
            tkMessageBox.showinfo(title, message)

        else: #if invalid file

            message = "You entered an invalid file type!"
            title = "Invalid file"
            tkMessageBox.showerror(title, message)

    except: #no filename or directory

        message = "Oops! You forgot to choose a file or save folder!"
        title = "Missing file or save folder"
        tkMessageBox.showerror(title, message)

def contrast(image):
    #contrasts image
    
    if(checkL(image)): #checks to see if L (one plate)
        returnImage = contrastPlate(image)
        return returnImage
    else:
        width,height = image.size
        greyImage = greyscale(image)
        greyPixels = greyImage.load()
        
        greyLImage = Image.new('L',greyImage.size)
        greyLPixels = greyLImage.load()
        
        for x in xrange(width):
            for y in xrange(height):
                #first value of the pixel (RGBA)
                #since greyscale all the values are the same (except a)
                greyLPixels[x,y] = greyPixels[x,y][0]
                
        greyContrast = contrastPlate(greyLImage) #contrast grey plate
        iPixels = image.load()

        gPixels = greyContrast.load()
        for x in xrange(width):
            for y in xrange(height):

                #grey value of the greyscale of same image
                gValue = gPixels[x,y]
                
                if(len(iPixels[x,y]) == 3): #RGB
                    r,g,b = iPixels[x,y]
                else: #RGBA
                    r,g,b,a = iPixels[x,y]
                    
                total = r+g+b

                #ratios of r,g,b with respect to each other
                #multipled by greyscale value to preserve ratios
                if(total > 0):
                    rRatio = (float(r)/total)*gValue
                    gRatio = (float(g)/total)*gValue
                    bRatio = (float(b)/total)*gValue
                    
                    iPixels[x,y] = int(rRatio),int(gRatio),int(bRatio),100
                else:
                    
                    iPixels[x,y] = r,g,b,100

        return brighten(image)

def findMean(histogram,length):
    #calculate mean
    
    average = 0
    count = 0
    for i in xrange(length):
        average += histogram[i]*i
        count += histogram[i]
    average /= count
    return average

def standardDeviation(histogram,length,mean):
    #calculate standard deviation

    sumOf = 0
    count = 0
    for i in xrange(length):
        deviation = (i - mean)
        sqDev = deviation**2
        sumOf += sqDev*histogram[i]
        count += histogram[i]
    standardDev = (sumOf/(count-1))**.5
    return standardDev

def equalize(histo):
    #returns dictionary of cumulative
    
    previous=(0,0) #keeps track of previous nonzero value (cumulative)
    cumulative = histo #cumulative totals with last one being # of pixels
    for i in xrange(len(histo)):
        if(previous[1] == 0 and histo[i] != 0): #assigns first value to previous
            previous = (i,histo[i])
        else:
            cumulative[i] = histo[i] + previous[1]
            previous = (i,histo[i])

    return cumulative

def generateHistogram(pixels, (width,height)):
    #returns list of intensities and how frequent of occurence

    intensities = [0]*256 #intensity range: 0-255

    for x in xrange(width):
        for y in xrange(height):
            intensities[pixels[x,y]] += 1

    return intensities

def histogramequal(histogram,cumulative,(width,height)):
    #equalizes the histogram
    
    mean = findMean(histogram,len(histogram))
    stdev = standardDeviation(histogram,len(histogram),mean)

    minIntensity = mean-stdev
    maxIntensity = mean+stdev
    
    for i in xrange(len(cumulative)):
        if (cumulative[i]>0):
            minimum = cumulative[i]
            break

    nValues = dict() #maps new values of intensity levels
    for j in xrange(len(cumulative)):
        if(cumulative[j] != 0):
            value = ((cumulative[j]-minimum)/(float(width*height)-minimum))*255
                            #maximum intensity-1
                            #(where intensity range is 0-256)
            nValues[j] = int(round(value))

    return nValues

def contrastPlate(image):
    #contrasts the plate

    histogram = generateHistogram(image.load(),image.size)
    cumulative = equalize(histogram)
    newValues = histogramequal(histogram,cumulative,image.size)
    
    pixels = image.load()
    width,height = image.size
    for x in xrange(width):
        for y in xrange(height):
            pixels[x,y] = newValues[pixels[x,y]] #assigns new equalized values
                                                #corresponding to original value
    return image

def brighten(image):
    #brightens the image

    pixels = image.load()
    width,height = image.size

    for x in xrange(width):
        for y in xrange(height):

            if(checkL(image)):
                pixels[x,y] = int(pixels[x,y]*3.25)
            elif(len(pixels[x,y]) == 3):
                r,g,b = pixels[x,y]
                pixels[x,y] = int(r*3.25), int(g*3.25), int(b*3.25)
            else:
                r,g,b,a = pixels[x,y]
                pixels[x,y] = int(r*3.25), int(g*3.25), int(b*3.25),a
                
    return image
        

############################Blur##########################

def wrapperBlur():
    #wrapper for blur function

    try:
        #file and directory to save into
        file = filtercanvas.data.filename
        saveFolder = filtercanvas.data.foldername
        
        if(isValidFilename(file)):
            
            image = Image.open(file)
            returnImage = blur(image)

            #save to saveFolder
            returnImage.show()
            fn = tuple(file.split('.'))
            returnImage.save("%s/Image-blur.%s"%(saveFolder,fn[-1]))

            #tells user when done saving
            message = "Edited image has been saved! You may exit browser!"
            title = "Finished!"
            tkMessageBox.showinfo(title, message)

        else: #if invalid file

            message = "You entered an invalid file type!"
            title = "Invalid file"
            tkMessageBox.showerror(title, message)

    except: #no filename or directory

        message = "Oops! You forgot to choose a file or save folder!"
        title = "Missing file or save folder"
        tkMessageBox.showerror(title, message)

def blur(image):
    #blur image
    
    if(checkL(image)): #L
        returnImage = blurColorPlate(image)
        
    else: #RGB or RGBA
        colValuesList = separateColors(image)
        r,g,b = blurPlates(colValuesList)
        returnImage = combine(image.size,r,g,b)
        
    return returnImage

def blurPlates(plates):
    #blur plates

    #blur all the colored plates
    blurredcolValues = [] 
    for image in plates:
        blurred = blurColorPlate(image)
        blurredcolValues.append(blurred)

    #corresponding plates to colors
    r = blurredcolValues[0]
    g = blurredcolValues[1]
    b = blurredcolValues[2]
    
    return r,g,b

def combine(size,r,g,b,a=100):
    #combine the plates of color values
    
    width,height = size
    rPixels,gPixels,bPixels = r.load(),g.load(),b.load()
    
    combined = Image.new('RGBA', size)
    cPixels = combined.load()
    
    for x in xrange(width):
        for y in xrange(height):
            cPixels[x,y] = (rPixels[x,y],gPixels[x,y],bPixels[x,y],a)
            
    return combined

def separateColors(image):
    #separates the colors in the image
    
    #assumes image is RGBA or RGB
    pixels = image.load()
    width,height = image.size

    #greyscale images containing r,g,b values
    rValues = Image.new('L',image.size)
    gValues = Image.new('L',image.size)
    bValues = Image.new('L',image.size)
    
    rPixels,gPixels,bPixels = rValues.load(),gValues.load(),bValues.load()

    for x in xrange(width):
        for y in xrange(height):
            
            if(len(pixels[0,0]) == 3): #RGB
                rPixels[x,y],gPixels[x,y],bPixels[x,y] = pixels[x,y]
            else: #RGBA
                rPixels[x,y],gPixels[x,y],bPixels[x,y],a = pixels[x,y]

    return [rValues,gValues,bValues]
        

def blurColorPlate(image):
    #blurs the single colored plate

    #return image is greyscale
    blurred = Image.new('L',image.size)
    #matrix used to blur
    cMatrix = [[1,1,1],
               [1,1,1],
               [1,1,1]]
    
    width, height = image.size
    center = (width/2, height/2)
    pixels = image.load()
    npixels = blurred.load()

    matrixL = len(cMatrix)
    halfOfmL = int(round(matrixL/2.))

    #applies the filter
    for startX in xrange(width):
        for startY in xrange(height):
            npixels[startX,startY] = pixels[startX,startY]

            value = applyBlur((startX,startY),cMatrix,npixels,image.size)

            npixels[startX,startY] = value
            
    return blurred
    
def applyBlur((x,y),matrix,pixels, size):
    #applies the blur filter with matrix

    width,height = size

    matrixL = len(matrix)
    halfOfmL = int(round(matrixL/2.))
    
    #calculate average value by averaging all the values surrounding
    #the pixel (includes the pixel itself) and returning the averaged
    #value
    averageG = 0
    count = 0
    
    for startX in xrange(x-halfOfmL,x+halfOfmL-1):
        for startY in xrange(y-halfOfmL,y+halfOfmL-1):

            if(0<=startX<width):
                if(0<=startY<height):

                    #calculate corresponding matrix value
                    dx, dy = startX-x, startY-y
                    mX, mY = halfOfmL+dx-1,halfOfmL+dy-1
                            
                    #calculates average
                    g = pixels[startX,startY]
                    averageG += g*matrix[mX][mY]
                    count += 1
            
    averageG /= count
    return averageG

###########################Sharpen##########################

def wrapperSharpen():
    #serves as wrapper for sharpen function

    try:
        #file and directory where it'll be saved
        file = filtercanvas.data.filename
        saveFolder = filtercanvas.data.foldername
        
        if(isValidFilename(file)):
            
            image = Image.open(file)
            returnImage = sharpen(image)

            #save to saveFolder
            returnImage.show()
            fn = tuple(file.split('.'))
            returnImage.save("%s/Image-sharpen.%s"%(saveFolder,fn[-1]))

            #tells user when done saving
            message = "Edited image has been saved! You may exit browser!"
            title = "Finished!"
            tkMessageBox.showinfo(title, message)

        else: #if invalid file

            message = "You entered an invalid file type!"
            title = "Invalid file"
            tkMessageBox.showerror(title, message)

    except: #no filename or directory

        message = "Oops! You forgot to choose a file or save folder!"
        title = "Missing file or save folder"
        tkMessageBox.showerror(title, message)

def sharpen(image):
    #sharpens image
    
    if(checkL(image)): #L
        returnImage = sharpenColorPlate(image)
        
    else: #RGB or RGBA
        colValuesList = separateColors(image)
        r,g,b = sharpenPlates(colValuesList)
        returnImage = combine(image.size,r,g,b)
        
    return returnImage

def sharpenPlates(plates):
    #sharpens the color plates

    #sharpen all the colored plates in list
    sharpenedcolValues = [] 
    for image in plates:
        sharpened = sharpenColorPlate(image)
        sharpenedcolValues.append(sharpened)

    #corresponding plates to colors
    r = sharpenedcolValues[0]
    g = sharpenedcolValues[1]
    b = sharpenedcolValues[2]
    
    return r,g,b

def sharpenColorPlate(image):
    #sharpens each individual plate

    #return image is greyscale
    sharpened = Image.new('L',image.size)
    
    #matrix adjusted after testing with images
    sMatrix = [[0,-1,0],
               [-1,3,-1],
               [0,-1,0]]
    
    width, height = image.size
    center = (width/2, height/2)
    pixels = image.load()
    npixels = sharpened.load()

    matrixL = len(sMatrix)
    halfOfmL = int(round(matrixL/2.))

    #applies the filter
    for startX in xrange(width):
        for startY in xrange(height):
            npixels[startX,startY] = pixels[startX,startY]

            if(startX>=halfOfmL and startY>=halfOfmL):
                value = applySharpen((startX,startY),sMatrix,pixels,image.size)

                npixels[startX,startY] = value
                
    return sharpened

def applySharpen((x,y),matrix,pixels,(width,height)):
    #applies the sharpen filter matrix

    matrixL = len(matrix)
    halfOfmL = matrixL/2
    
    #calculate value by muliplying the original value of the pixel
    #then subtracting it by the pixel values of its surroundings
    #(does not include diagonals)
    gIntensity = 0

    for startX in xrange(x-halfOfmL,x+halfOfmL):
        for startY in xrange(y-halfOfmL,y+halfOfmL):
            
            if(0<=startX<width):
                if(0<=startY<height):

                    #calculate corresponding matrix value
                    dx, dy = startX-x, startY-y
                    mX, mY = halfOfmL+dx,halfOfmL+dy
                            
                    #calculates intensity
                    g = pixels[startX,startY]
                    gIntensity += g*matrix[mX][mY]

    return gIntensity

###########################Pencil##########################

def wrapperPencil():
    #serves as wrapper for pencil function

    try:
        #file and directory it's to be saved to
        file = filtercanvas.data.filename
        saveFolder = filtercanvas.data.foldername
        
        if(isValidFilename(file)):
            
            image = Image.open(file)
            returnImage = pencil(image)

            #file saved to saveFolder
            returnImage.show()
            fn = tuple(file.split('.'))
            returnImage.save("%s/Image-pencil.%s"%(saveFolder,fn[-1]))
            
            #tells user when done saving
            message = "Edited image has been saved! You may exit browser!"
            title = "Finished!"
            tkMessageBox.showinfo(title, message)

        else: #if file invalid

            message = "You entered an invalid file type!"
            title = "Invalid file"
            tkMessageBox.showerror(title, message)

    except: #no filename or directory

        message = "Oops! You forgot to choose a file or save folder!"
        title = "Missing file or save folder"
        tkMessageBox.showerror(title, message)

def pencil(image):
    #pencils image

    #contrasts image first to make lights and darks more apparent
    #helps enhance the filter
    image = contrast(image)
    
    if(checkL(image)): #L
        returnImage = pencilColorPlate(image)
        
    else: #RGB or RGBA
        colValuesList = separateColors(image)
        r,g,b = pencilPlates(colValuesList)
        returnImage = combine(image.size,r,g,b)

    #puts the image onto a silverPlate
    returnImage = silverPlate(returnImage)
    
    return returnImage

def silverPlate(image):
    #silverPlates the image, giving a look as if its greyed
    #(but unlike greyscale)

    returnImage = Image.new('RGBA',image.size) 
    rPixels = returnImage.load()

    image = greyscale(image)
    pixels = image.load()
    width,height = image.size

    for x in xrange(width):
        for y in xrange(height):

            #if greyscale image is not L then gets the first value
            #because all values of greyscale are the same
            if(type(pixels[x,y]) != int):
                gValue = pixels[x,y][0]
            else:
                gValue = pixels[x,y]
            
            if(gValue != 0):
                averageV = gValue/2
                rPixels[x,y] = averageV, averageV, averageV, 100

    return returnImage

def pencilPlates(plates):
    #pencils the color plates 

    #pencils all the colored plates
    penciledcolValues = [] 
    for image in plates:
        penciled = pencilColorPlate(image)
        penciledcolValues.append(penciled)

    #corresponding plates to colors
    r = penciledcolValues[0]
    g = penciledcolValues[1]
    b = penciledcolValues[2]
    
    return r,g,b

def pencilColorPlate(image):
    #pencils individual color plates

    #return image is greyscale
    penciled = Image.new('L',image.size)
    
    #matrix adjusted after testing with images
    pMatrix = [[-4,-4,0],
               [-4,12,.5],
               [0,.5,.5]]
    
    width, height = image.size
    center = (width/2, height/2)
    pixels = image.load()
    npixels = penciled.load()

    matrixL = len(pMatrix)
    halfOfmL = int(round(matrixL/2.))

    #applies the filter
    for startX in xrange(width):
        for startY in xrange(height):
            npixels[startX,startY] = pixels[startX,startY]

            if(startX>=halfOfmL and startY>=halfOfmL):

                value = applyPenciled((startX,startY),pMatrix,pixels,image.size)

                npixels[startX,startY] = value
                
    return penciled

def applyPenciled((x,y),matrix,pixels,(width,height)):
    #applies the pencil filter

    matrixL = len(matrix)
    halfOfmL = int(round(matrixL/2.))
    
    #calculate value by muliplying the original value
    #then subtracting or adding to this value by surroundings
    intensityG = 0

    for startX in xrange(x-halfOfmL,x+halfOfmL-1):
        for startY in xrange(y-halfOfmL,y+halfOfmL-1):

            if(0<=startX<width):
                if(0<=startY<height):
                    #calculate corresponding matrix value
                    dx, dy = startX-x, startY-y
                    mX, mY = halfOfmL+dx-1,halfOfmL+dy-1
                            
                    #calculates intensity
                    g = pixels[startX,startY]
                    intensityG += g*matrix[mX][mY]

    return intensityG


############################Tile##########################

def wrapperTiled():
    #serves as wrapper for tiled function

    try:
        #file and directory to be saved to
        file = filtercanvas.data.filename
        saveFolder = filtercanvas.data.foldername

        #number of rows and cols image will be multipled by
        rows = filtercanvas.data.tileRows
        cols = filtercanvas.data.tileCols
        
        if(isValidFilename(file)):
            
            image = Image.open(file)
            returnImage = tiled(image,rows,cols)

            #save to saveFolder
            returnImage.show()
            fn = tuple(file.split('.'))
            returnImage.save("%s/Image-tile.%s"%(saveFolder,fn[-1]))

            #tells user when done saving
            message = "Edited image has been saved! You may exit browser!"
            title = "Finished!"
            tkMessageBox.showinfo(title, message)

        else: #if file invalid

            message = "You entered an invalid file type!"
            title = "Invalid file"
            tkMessageBox.showerror(title, message)

    except: #no filename or directory

        message = "Oops! You forgot to choose a file or save folder!"
        title = "Missing file or save folder"
        tkMessageBox.showerror(title, message)

def tiled(image,rows,cols,border=0):
    #tiles the image, will allow border if specified always
    #returns an RGBA image
    
    (iWidth,iHeight) = image.size
    
    #width corresponds to cols
    #height corresponds to rows
    (tWidth,tHeight) = ((iWidth*cols)+(border*(cols+1)),(iHeight*rows)+(border*(rows+1)))
    tiled = Image.new('RGBA', (tWidth,tHeight))
    iPixels, tPixels = image.load(), tiled.load()
    
    for row in xrange(rows):
        for col in xrange(cols):
            for x in xrange(iWidth):
                for y in xrange(iHeight):
                    newX = ((iWidth*col)+x)+(border*(col+1))
                    newY = ((iHeight*row)+y)+(border*(row+1))

                    #assigns pixel values
                    #check to see if image is 'L' greyscale image
                    if(type(iPixels[x,y]) == int):
                        tPixels[newX,newY] = (iPixels[x,y],iPixels[x,y],
                                              iPixels[x,y],100)
                        
                    #check to see if image is 'RGB' image (3 values)
                    elif(len(iPixels[x,y]) == 3):
                        r,g,b = iPixels[x,y]
                        tPixels[newX,newY] = (r,g,b, 100)
                    else: #RGBA
                        tPixels[newX,newY] = iPixels[x,y]
                        
    return tiled

def checkL(image):
    #checks to see if L image
    
    pixels = image.load()
    if(type(pixels[0,0]) == int):
        return True
    return False

############################Technicolor##########################

def wrapperTechnicolor():
    #serves as wrapper for technicolor function

    try:
        #file and directory to be saved to
        file = filtercanvas.data.filename
        saveFolder = filtercanvas.data.foldername
        
        if(isValidFilename(file)):
            
            image = Image.open(file)
            colored = technicolorTiles(image)

            #save to saveFolder
            colored.show()
            fn = tuple(file.split('.'))
            colored.save("%s/Image-technicolor.%s"%(saveFolder,fn[-1]))

            #tells user when done saving
            message = "Edited image has been saved! You may exit browser!"
            title = "Finished!"
            tkMessageBox.showinfo(title, message)

        else: #if file is invalid

            message = "You entered an invalid file type!"
            title = "Invalid file"
            tkMessageBox.showerror(title, message)

    except: #no filename or directory

        message = "Oops! You forgot to choose a file or save folder!"
        title = "Missing file or save folder"
        tkMessageBox.showerror(title, message)

def technicolorTiles(image):
    #technicolors the image (2x2 with different colors)
    
    #rgba values for different colors
    width,height = image.size

    #primary colors (RGBA):
    green = (0,139,0,50)
    blue = (100, 149, 237, 50)
    red = (220, 20, 60, 50)
    purple = (132, 112, 255, 50)

    #images of solid color filters:
    gFilter = Image.new('RGBA',image.size,green)
    rFilter = Image.new('RGBA',image.size,red)
    bFilter = Image.new('RGBA',image.size,blue)
    pFilter = Image.new('RGBA',image.size,purple)

    colors = [gFilter,pFilter,bFilter,rFilter]
    filtered = transpose(colors,image)

    popArt = assemble(filtered,2,2)
    
    return popArt
    
def transpose(ListOfFilters,image):
    #returns a list of filtered images
    
    sWidth,sHeight = image.size
    image = greyscale(image)
    
    filtered = []
    for filt in ListOfFilters:
        fPixels = filt.load()
        iPixels = image.load()
        for x in xrange(sWidth):
            for y in xrange(sHeight):
                r,g,b,a = fPixels[x,y]

                if(type(iPixels[x,y]) == int): #L
                    ratio = iPixels[x,y]/float(256)
                else: #RGB or RGBA
                    ratio = iPixels[x,y][0]/float(256)
                    #takes first value because all values are same since
                    #greyscale
                
                fPixels[x,y] = (int(r*ratio),int(g*ratio),
                                int(b*ratio),a)
        filtered.append(filt)
        
    return filtered

#############################Paint Program##########################

#reimported to show that all this is used in paint
#(design choice)
import Tkinter as tk
from PIL import Image, ImageTk
import tkFileDialog
import tkMessageBox
import tkFont

def PaintmousePressed(event):
    #records coordinates of where the user clicked
    #which is used to filter that specific part of the image
    
    if(Paintcanvas.data.isFeatureOn and
        Paintcanvas.data.isPressed == False and
       0<=event.x<=Paintcanvas.data.image.width() and
       50<=event.y<=Paintcanvas.data.image.height()+50):
        
        Paintcanvas.data.mouseStartPosition = (event.x,event.y)
        
    Paintcanvas.data.mousePosition = (event.x,event.y) 
    Paintcanvas.data.isPressed = True
    
    PaintredrawAll()

def PaintmouseMoved(event):
    #records coordinates of where the user is moving the mouse
    #used to draw the rectangle that the user can view
    #so they know where the image will be filtered
    
    if(Paintcanvas.data.isPressed):
        Paintcanvas.data.mousePosition = (event.x,event.y)
        
    PaintredrawAll()

def PaintmouseReleased(event):
    #records coordinates of where the user released the mouse
    #used to get the final coordinates of the rectangle
    #that will be filtered
    
    Paintcanvas.data.isPressed = False
    Paintcanvas.data.mousePosition = (event.x,event.y)
    
    PaintredrawAll()

def cropInRespect():
    #crops the image at the part where the user wants filtered

    image = Paintcanvas.data.image #PhotoImage image

    #coordinates of where the rectangle was drawn
    #(where user wants filtered)
    startx,starty,finalx,finaly = Paintcanvas.data.rectangleCoord

    #coordinates of where the image is placed in respect to the canvas
    leftEdgeOfX = 0
    rightEdgeOfX = image.width()
    topEdgeOfY = 50
    bottomEdgeOfY = image.height()+50

    #makes sure the rectangle is in the bounds of the image or else
    #ignored.
    if(leftEdgeOfX <= startx <= rightEdgeOfX and
       topEdgeOfY <= starty <= bottomEdgeOfY and
       leftEdgeOfX <= finalx <= rightEdgeOfX and
       topEdgeOfY <= finaly <= bottomEdgeOfY):

        #finds the minimum and maximum (this way, user can move box
        #southeast or northwest
        minX = min(startx,finalx)
        maxX = max(startx,finalx)
        minY = min(starty,finaly)
        maxY = max(starty,finaly)

        #coordinates of the box in respect to the image
        Paintcanvas.data.imageCoord = (minX-leftEdgeOfX,minY-topEdgeOfY,
                                       maxX-leftEdgeOfX,maxY-topEdgeOfY)
        
        imageCoord = Paintcanvas.data.imageCoord
        cropped = Paintcanvas.data.pilImage.crop(imageCoord)
        
        return cropped

def pasteToImage(filtered):
    #pastes the filtered part into the pilImage
    #which will be converted to a PhotoImage to be
    #displayed in canvas
    
    pilPixels = Paintcanvas.data.pilImage.load()
    filteredPixels = filtered.load()
    x1,y1,x2,y2 = Paintcanvas.data.imageCoord
    
    for x in xrange(x1,x2):
        for y in xrange(y1,y2):
            i = x-x1
            j = y-y1
            pilPixels[x,y] = filteredPixels[i,j]

def error():

    message = 'Oh no! Something went wrong! Window closing...'
    title = 'Error'
    tkMessageBox.showerror(title=title, message=message)

    pWindow.destroy()
    pWindow.mainloop()

def blurPressed():
    #is called when blur is on, which will blur the specific
    #region the user desires to be blurred

    try:
        #coordinates of where the rectangle was drawn
        #(where user wants filtered)
        startx,starty,finalx,finaly = Paintcanvas.data.rectangleCoord

        #turn to PIL Image and blur
        if(Paintcanvas.data.isBlur and startx != finalx and
           starty != finaly):
                
            cropped = cropInRespect()
            blurred = blur(cropped)

            pasteToImage(blurred)

            #creates new PhotoImage with the filtered image
            pilImage = Paintcanvas.data.pilImage
            Paintcanvas.data.image = ImageTk.PhotoImage(pilImage)

            #reset mousePositions
            Paintcanvas.data.mouseStartPosition = (-1,-1)
            Paintcanvas.data.mousePosition = (-1,-1)
            

        #turn off everything except blur and feature on
        Paintcanvas.data.isFeatureOn = True
        Paintcanvas.data.isBlur = True
        Paintcanvas.data.isSharpen = False
        Paintcanvas.data.isGreyscale = False
        Paintcanvas.data.isSepia = False
        Paintcanvas.data.isPencil = False
        
        #select and deselect buttons
        Paintcanvas.data.blur.select()
        Paintcanvas.data.sharpen.deselect()
        Paintcanvas.data.greyscale.deselect()
        Paintcanvas.data.sepia.deselect()
        Paintcanvas.data.pencil.deselect()

    except:

        error()
    

def sharpenPressed():
    #is called when sharpen is on, which will sharpen the specific
    #region the user desires to be sharpened

    try:
        #coordinates of where the rectangle was drawn
        #(where user wants filtered)
        startx,starty,finalx,finaly = Paintcanvas.data.rectangleCoord

        #turn to PIL Image and sharpen
        if(Paintcanvas.data.isSharpen and startx != finalx and
           starty != finaly):
                
            cropped = cropInRespect()
            sharpened = sharpen(cropped)

            pasteToImage(sharpened)

            #creates new PhotoImage with the filtered image
            pilImage = Paintcanvas.data.pilImage
            Paintcanvas.data.image = ImageTk.PhotoImage(pilImage)

            #reset mousePositions
            Paintcanvas.data.mouseStartPosition = (-1,-1)
            Paintcanvas.data.mousePosition = (-1,-1)

        #turn off everything except sharpen and feature on
        Paintcanvas.data.isFeatureOn = True
        Paintcanvas.data.isSharpen = True
        Paintcanvas.data.isBlur = False
        Paintcanvas.data.isGreyscale = False
        Paintcanvas.data.isSepia = False
        Paintcanvas.data.isPencil = False

        #select and deselect buttons
        Paintcanvas.data.sharpen.select()
        Paintcanvas.data.blur.deselect()
        Paintcanvas.data.greyscale.deselect()
        Paintcanvas.data.sepia.deselect()
        Paintcanvas.data.pencil.deselect()

    except:

        error()

def greyscalePressed():
    #is called when greyscale is on, which will greyscale the specific
    #region the user desires to be greyscaled

    try:
        #coordinates of where the rectangle was drawn
        #(where user wants filtered)
        startx,starty,finalx,finaly = Paintcanvas.data.rectangleCoord

        #turn to PIL Image and greyscale
        if(Paintcanvas.data.isGreyscale and startx != finalx and
           starty != finaly):
                
            cropped = cropInRespect()
            greyscaled = greyscale(cropped)

            pasteToImage(greyscaled)

            #creates new PhotoImage with the filtered image
            pilImage = Paintcanvas.data.pilImage
            Paintcanvas.data.image = ImageTk.PhotoImage(pilImage)

            #reset mousePositions
            Paintcanvas.data.mouseStartPosition = (-1,-1)
            Paintcanvas.data.mousePosition = (-1,-1)

        #turn off everything except greyscale and feature on
        Paintcanvas.data.isFeatureOn = True
        Paintcanvas.data.isGreyscale = True
        Paintcanvas.data.isBlur = False
        Paintcanvas.data.isSharpen = False
        Paintcanvas.data.isSepia = False
        Paintcanvas.data.isPencil = False

        #select and deselect buttons
        Paintcanvas.data.greyscale.select()
        Paintcanvas.data.blur.deselect()
        Paintcanvas.data.sharpen.deselect()
        Paintcanvas.data.sepia.deselect()
        Paintcanvas.data.pencil.deselect()

    except:

        error()

def sepiaPressed():
    #is called when sepia is on, which will sepia the specific
    #region the user desires to be sepiaed

    try:
        #coordinates of where the rectangle was drawn
        #(where user wants filtered)
        startx,starty,finalx,finaly = Paintcanvas.data.rectangleCoord

        #turn to PIL Image and sepia
        if(Paintcanvas.data.isSepia and startx != finalx and
           starty != finaly):
                
            cropped = cropInRespect()
            sepiaed = sepia(cropped)

            pasteToImage(sepiaed)

            #creates new PhotoImage with the filtered image
            pilImage = Paintcanvas.data.pilImage
            Paintcanvas.data.image = ImageTk.PhotoImage(pilImage)

            #reset mousePositions
            Paintcanvas.data.mouseStartPosition = (-1,-1)
            Paintcanvas.data.mousePosition = (-1,-1)

        #turn off everything except sepia and feature on
        Paintcanvas.data.isFeatureOn = True
        Paintcanvas.data.isSepia = True
        Paintcanvas.data.isBlur = False
        Paintcanvas.data.isSharpen = False
        Paintcanvas.data.isGreyscale = False
        Paintcanvas.data.isPencil = False

        #select and deselect buttons
        Paintcanvas.data.sepia.select()
        Paintcanvas.data.blur.deselect()
        Paintcanvas.data.sharpen.deselect()
        Paintcanvas.data.greyscale.deselect()
        Paintcanvas.data.pencil.deselect()

    except:

        error()

def pencilPressed():
    #is called when pencil is on, which will pencil the specific
    #region the user desires to be penciled

    try:
        #coordinates of where the rectangle was drawn
        #(where user wants filtered)
        startx,starty,finalx,finaly = Paintcanvas.data.rectangleCoord

        #turn to PIL Image and pencil
        if(Paintcanvas.data.isPencil and startx != finalx and
           starty != finaly):
                
            cropped = cropInRespect()
            penciled = pencil(cropped)

            pasteToImage(penciled)

            #creates new PhotoImage with the filtered image
            pilImage = Paintcanvas.data.pilImage
            Paintcanvas.data.image = ImageTk.PhotoImage(pilImage)

            #reset mousePositions
            Paintcanvas.data.mouseStartPosition = (-1,-1)
            Paintcanvas.data.mousePosition = (-1,-1)
            

        #turn off everything except pencil and feature on
        Paintcanvas.data.isFeatureOn = True
        Paintcanvas.data.isPencil = True
        Paintcanvas.data.isBlur = False
        Paintcanvas.data.isSharpen = False
        Paintcanvas.data.isGreyscale = False
        Paintcanvas.data.isSepia = False

        #select and deselect buttons
        Paintcanvas.data.pencil.select()
        Paintcanvas.data.sharpen.deselect()
        Paintcanvas.data.greyscale.deselect()
        Paintcanvas.data.sepia.deselect()
        Paintcanvas.data.blur.deselect()

    except:

        error()

def Paintfinish():
    #user done editing the image
    Paintcanvas.data.isFinished = True
    
def saveFiltered():
    #saves image

    #saves to same folder
    fn = tuple(Paintcanvas.data.filename.split('.'))
    Paintcanvas.data.pilImage.save("%s-edited.%s"%fn)

    #tells user when done saving
    message = "Edited image has been saved! You may exit browser!"
    title = "Finished!"
    tkMessageBox.showinfo(title, message)

    Paintcanvas.data.saved = True

def PaintredrawAll():
    #draws canvas
    
    Paintcanvas.delete(tk.ALL)
    
    #draw image
    image = Paintcanvas.data.image
    imageSize = ((image.width(),image.height()))
    Paintcanvas.create_image(0,50,image=image,anchor='nw')

    if(Paintcanvas.data.isFinished and Paintcanvas.data.saved==False):
        #saves only once
        saveFiltered()

    else:

        startx,starty = Paintcanvas.data.mouseStartPosition
        finalx,finaly = Paintcanvas.data.mousePosition
        
        leftEdgeOfX = 0
        rightEdgeOfX = image.width()
        topEdgeOfY = 50
        bottomEdgeOfY = image.height()+50
        
        #draw selection rectangle
        if(Paintcanvas.data.isRectangle):
            if(Paintcanvas.data.isPressed and
               leftEdgeOfX <= startx <= rightEdgeOfX and
               topEdgeOfY <= starty <= bottomEdgeOfY and
               leftEdgeOfX <= finalx <= rightEdgeOfX and
               topEdgeOfY <= finaly <= bottomEdgeOfY):

                Paintcanvas.create_rectangle(startx,starty,finalx,finaly,
                                             fill="", outline="black")
                minX = min(startx,finalx)
                maxX = max(startx,finalx)
                minY = min(starty,finaly)
                maxY = max(starty,finaly)
                Paintcanvas.data.rectangleCoord = (minX,minY,maxX,maxY)
                
            else: #not pressed, so filter
                
                if(Paintcanvas.data.mouseStartPosition[0] > 0 and
                   Paintcanvas.data.mousePosition[0] > 0):
                    if(Paintcanvas.data.isBlur):
                       blurPressed()

                    elif(Paintcanvas.data.isSharpen):
                       sharpenPressed()

                    elif(Paintcanvas.data.isGreyscale):
                       greyscalePressed()

                    elif(Paintcanvas.data.isSepia):
                        sepiaPressed()

                    elif(Paintcanvas.data.isPencil):
                        pencilPressed()

def Paintinit(root,Paintcanvas):

    #finishing variables
    Paintcanvas.data.isFinished = False
    Paintcanvas.data.saved = False

    #on and off of features
    Paintcanvas.data.isBlur = False
    Paintcanvas.data.isSharpen = False
    Paintcanvas.data.isGreyscale = False
    Paintcanvas.data.isSepia = False
    Paintcanvas.data.isPencil = False
    Paintcanvas.data.isFeatureOn = False

    #rectangle or circle
    Paintcanvas.data.isRectangle = True

    #mouse on and off 
    Paintcanvas.data.isPressed = False

    #different mouse coordinates
    Paintcanvas.data.mouseStartPosition = (-1,-1)
    Paintcanvas.data.mousePosition = (-1,-1)
    Paintcanvas.data.rectangleCoord = (-1,-1,-1,-1)
    Paintcanvas.data.imageCoord = (-1,-1,-1,-1)

    #filter buttons
    buttonFrame = tk.Frame(root)
    #blur
    Paintcanvas.data.blur = tk.Checkbutton(buttonFrame, text="blur",
                                           command=blurPressed)
    Paintcanvas.data.blur.grid(row=0,column=0)
    #sharpen
    Paintcanvas.data.sharpen = tk.Checkbutton(buttonFrame,
                                              text="sharpen",
                                              command=sharpenPressed)
    Paintcanvas.data.sharpen.grid(row=0,column=1)
    #greyscale
    Paintcanvas.data.greyscale = tk.Checkbutton(buttonFrame,
                                                text="greyscale",
                                                command=greyscalePressed)
    Paintcanvas.data.greyscale.grid(row=0,column=2)
    #sepia
    Paintcanvas.data.sepia = tk.Checkbutton(buttonFrame,text="sepia",
                                            command=sepiaPressed)
    Paintcanvas.data.sepia.grid(row=1,column=0)
    #pencil
    Paintcanvas.data.pencil = tk.Checkbutton(buttonFrame,text="pencil",
                                             command=pencilPressed)
    Paintcanvas.data.pencil.grid(row=1,column=1)
    
    #done Button
    Paintcanvas.data.done = tk.Button(buttonFrame,text="Done!",
                                      command=Paintfinish)
    Paintcanvas.data.done.grid(row=2,column=1)
    
    buttonFrame.pack(side=tk.TOP)
    Paintcanvas.pack()

    
    #input image
    Paintcanvas.data.pilImage = Image.open(Paintcanvas.data.filename)

    PaintredrawAll()

def Paintrun():
    
    global Paintcanvas
    global pWindow

    #creates separate window
    pWindow = tk.Toplevel()

    try:
        #gets file and puts it into the canvas
        filename = tkFileDialog.askopenfilename()
        
        if(len(filename)>0): #filename exists
            image = ImageTk.PhotoImage(file=filename)
            pWindow.geometry('%dx%d' % (image.width(),image.height()+100))
            Paintcanvas = tk.Canvas(pWindow,width=image.width(),
                                    height=image.height()+100)

            pWindow.resizable(0,0) #locks, not allowed to resize

            pWindow.canvas = Paintcanvas.canvas = Paintcanvas
            
            # Set up canvas data and call init
            class Struct: pass
            Paintcanvas.data = Struct()

            #input image and its info
            Paintcanvas.data.width = image.width()
            Paintcanvas.data.height = image.height()
            Paintcanvas.data.filename = filename
            Paintcanvas.data.image = image
            
            Paintinit(pWindow,Paintcanvas)
            
            # set up events
            pWindow.bind("<Button-1>", PaintmousePressed)
            pWindow.bind("<Motion>", PaintmouseMoved)
            Paintcanvas.bind("<B1-Motion>", PaintmouseMoved)
            pWindow.bind("<B1-ButtonRelease>", PaintmouseReleased)

    except: #didn't select a file

        message = "You didn't select a file to edit!"
        title = "No file selected!"
        tkMessageBox.showerror(title, message)
        pWindow.destroy()
        
    pWindow.mainloop()
        

#############################GUI##########################

#reimported to show that all this is used in gui
#(design choice)
import Tkinter as tk
from PIL import Image, ImageTk
import tkFileDialog
import tkSimpleDialog

def splashScreen():
    #splash screen with title, andrewid

    #buttons for the window:
    buttonFont = splashcanvas.data.buttonFont
    splashcanvas.data.enterB = tk.Button(splashcanvas, text='ENTER',
                                         command=optionScreen,
                                         font=buttonFont)
    
    #draw image
    splashcanvas.create_image(0,0,image=splashcanvas.data.topbackground,
                              anchor='nw')

    #draw buttons
    titleFont = splashcanvas.data.titleFont
    splashcanvas.create_text(splashcanvas.data.width/2,
                             (splashcanvas.data.height/5)*2,
                               text='Fig.',font=titleFont)

    title2Font = tkFont.Font(family='American Typewriter',
                             size=35)
    splashcanvas.create_text(splashcanvas.data.width/2,
                             (splashcanvas.data.height/5)*3,
                               text='czeng',font=title2Font)

    splashcanvas.create_window(splashcanvas.data.width/2,
                               (splashcanvas.data.height/5)*4,
                                window=splashcanvas.data.enterB)

def quitNow():
    #quits entire program including the option window

    message = 'Are you sure you want to exit program?'
    title = 'Quit'
    response = tkMessageBox.askquestion(title, message)

    if(str(response)=='yes'):

        splashcanvas.data.root.destroy() #destroy root window
        splashcanvas.data.root.mainloop()  


def optionScreen():
    
    #deletes buttons
    splashcanvas.data.enterB.destroy()

    #buttons for option screen
    buttonFont = splashcanvas.data.buttonFont
    splashcanvas.data.gorskiiB = tk.Button(splashcanvas,
                                           text='Prokudin-Gorskii\'s Negatives',
                                           command=gorskiiWindow,
                                           font=buttonFont)
    splashcanvas.data.filterB = tk.Button(splashcanvas,
                                          text='I\'d like to filter my photo!',
                                          command=filterWindow,
                                          font=buttonFont)
    
    message = 'I only want to filter some of my photo!'
    splashcanvas.data.paintB = tk.Button(splashcanvas,
                                         text=message,
                                         command=Paintrun,
                                         font=buttonFont)

    splashcanvas.data.quitB = tk.Button(splashcanvas,
                                        text='QUIT',
                                        command=quitNow,
                                        font=buttonFont)

    #text and background image
    splashcanvas.create_image(0,0,image=splashcanvas.data.topbackground,
                              anchor='nw')

    titleFont = splashcanvas.data.titleFont    
    splashcanvas.create_text(splashcanvas.data.width/2,
                             (splashcanvas.data.height/5)+5,
                             text='Fig.',font=titleFont)

    #creates buttons
    splashcanvas.create_window(splashcanvas.data.width/2,
                               int((splashcanvas.data.height/5)*2.5),
                               window=splashcanvas.data.gorskiiB)
    splashcanvas.create_window(splashcanvas.data.width/2,
                               (splashcanvas.data.height/5)*3,
                               window=splashcanvas.data.filterB)
    splashcanvas.create_window(splashcanvas.data.width/2,
                               int((splashcanvas.data.height/5)*3.5),
                               window=splashcanvas.data.paintB)
    splashcanvas.create_window(splashcanvas.data.width/2,
                               (splashcanvas.data.height/5)*4,
                               window=splashcanvas.data.quitB)
    

def gorskiiScreen():
    #screen with all the options for gorskii negatives, creating negatives
    #and creating then realigning

    #buttons for gorskii option screen
    buttonFont = gorskiicanvas.data.buttonFont
    gorskiicanvas.data.alignB = tk.Button(gorskiicanvas,
                                          text='I have the negatives!',
                                          command=alignScreen,
                                          font=buttonFont)
    message = 'Create negatives from my photo!'
    gorskiicanvas.data.negativeB = tk.Button(gorskiicanvas,
                                             text=message,
                                             command=negativeScreen,
                                             font=buttonFont)
    message1 = 'Create negatives and realign the images!'
    gorskiicanvas.data.realignB = tk.Button(gorskiicanvas,
                                            text=message1,
                                            command=realignScreen,
                                            font=buttonFont)

    #text and background image
    gorskiicanvas.create_image(0,0,image=gorskiicanvas.data.background,
                               anchor='nw')

    titleFont = gorskiicanvas.data.titleFont
    gorskiicanvas.create_text(gorskiicanvas.data.width/2,
                              (gorskiicanvas.data.height/5)+5,
                              text='Fig.',font=titleFont,
                              fill='navy')

    titleFont = gorskiicanvas.data.title2Font
    gorskiicanvas.create_text(gorskiicanvas.data.width/2,
                              (gorskiicanvas.data.height/5)*2,
                              text='Prokudin-Gorskii\'s Negatives',
                              font=titleFont,fill='navy')

    #creates buttons
    gorskiicanvas.create_window(gorskiicanvas.data.width/2,
                                (gorskiicanvas.data.height/5)*3,
                                 window=gorskiicanvas.data.alignB)
    gorskiicanvas.create_window(gorskiicanvas.data.width/2,
                                int((gorskiicanvas.data.height/5)*3.5),
                                 window=gorskiicanvas.data.negativeB)
    gorskiicanvas.create_window(gorskiicanvas.data.width/2,
                                (gorskiicanvas.data.height/5)*4,
                                 window=gorskiicanvas.data.realignB)

def gorskiiopenPath():
    #gets the filepath of the image
    
    gorskiicanvas.data.filename = tkFileDialog.askopenfilename()


def gorskiisavePath():
    #gets the path for the directory to be saved in
    
    gorskiicanvas.data.foldername = tkFileDialog.askdirectory()

def alignScreen():
    #screen shown when user wants to align negatives

    #deletes buttons
    gorskiicanvas.data.alignB.destroy()
    gorskiicanvas.data.negativeB.destroy()
    gorskiicanvas.data.realignB.destroy()

    #buttons for gorskii option screen
    buttonFont = gorskiicanvas.data.buttonFont
    gorskiicanvas.data.aOpenB = tk.Button(gorskiicanvas,
                                           text='Browse for negatives!',
                                          command=gorskiiopenPath,
                                          font=buttonFont)
    gorskiicanvas.data.aSaveB = tk.Button(gorskiicanvas,
                                          text='Browse for save path!',
                                         command=gorskiisavePath,
                                         font=buttonFont)
    gorskiicanvas.data.aReadyB = tk.Button(gorskiicanvas,
                                           text='Ready!',
                                           command=wrapperAlignNegatives,
                                           font=buttonFont)

    #text and background image
    gorskiicanvas.create_image(0,0,image=gorskiicanvas.data.background,
                               anchor='nw')

    titleFont = gorskiicanvas.data.titleFont
    gorskiicanvas.create_text(gorskiicanvas.data.width/2,
                              (gorskiicanvas.data.height/5)+5,
                              text='Fig.',font=titleFont,
                              fill='navy')

    title2Font = gorskiicanvas.data.title2Font
    gorskiicanvas.create_text(gorskiicanvas.data.width/2,
                              int((gorskiicanvas.data.height/5)*1.5),
                              text='Prokudin-Gorskii\'s Negatives',
                              font=title2Font,fill='navy')

    title3Font = gorskiicanvas.data.title3Font
    gorskiicanvas.create_text(gorskiicanvas.data.width/2,
                              (gorskiicanvas.data.height/5)*2,
                              text='I have negatives!',
                              font=title3Font,fill='navy')
    
    #creates buttons
    gorskiicanvas.create_window(gorskiicanvas.data.width/2,
                                (gorskiicanvas.data.height/5)*3,
                                window=gorskiicanvas.data.aOpenB)
    gorskiicanvas.create_window(gorskiicanvas.data.width/2,
                                int((gorskiicanvas.data.height/5)*3.5),
                                window=gorskiicanvas.data.aSaveB)
    gorskiicanvas.create_window(gorskiicanvas.data.width/2,
                                (gorskiicanvas.data.height/5)*4,
                                window=gorskiicanvas.data.aReadyB)

def negativeScreen():
    #screen shown when user wants to make negative from image
                       
    #deletes buttons
    gorskiicanvas.data.alignB.destroy()
    gorskiicanvas.data.negativeB.destroy()
    gorskiicanvas.data.realignB.destroy()

    #buttons for gorskii option screen
    buttonFont = gorskiicanvas.data.buttonFont
    gorskiicanvas.data.aOpenB = tk.Button(gorskiicanvas,
                                           text='Browse for photo!',
                                          command=gorskiiopenPath,
                                          font=buttonFont)
    gorskiicanvas.data.aSaveB = tk.Button(gorskiicanvas,
                                          text='Browse for save path!',
                                         command=gorskiisavePath,
                                         font=buttonFont)
    gorskiicanvas.data.aReadyB = tk.Button(gorskiicanvas,
                                           text='Ready!',
                                           command=wrapperNegative,
                                           font=buttonFont)

    #text and background image
    gorskiicanvas.create_image(0,0,image=gorskiicanvas.data.background,
                               anchor='nw')

    titleFont = gorskiicanvas.data.titleFont
    gorskiicanvas.create_text(gorskiicanvas.data.width/2,
                              (gorskiicanvas.data.height/5)+5,
                              text='Fig.',font=titleFont,
                              fill='navy')

    title2Font = gorskiicanvas.data.title2Font
    gorskiicanvas.create_text(gorskiicanvas.data.width/2,
                              int((gorskiicanvas.data.height/5)*1.5),
                              text='Prokudin-Gorskii\'s Negatives',
                              font=title2Font,fill='navy')

    title3Font = gorskiicanvas.data.title3Font
    gorskiicanvas.create_text(gorskiicanvas.data.width/2,
                              (gorskiicanvas.data.height/5)*2,
                              text='Create negatives from my photo!',
                              font=title3Font,fill='navy')
    
    
    #creates buttons
    gorskiicanvas.create_window(gorskiicanvas.data.width/2,
                                (gorskiicanvas.data.height/5)*3,
                                window=gorskiicanvas.data.aOpenB)
    gorskiicanvas.create_window(gorskiicanvas.data.width/2,
                                int((gorskiicanvas.data.height/5)*3.5),
                                window=gorskiicanvas.data.aSaveB)
    gorskiicanvas.create_window(gorskiicanvas.data.width/2,
                                (gorskiicanvas.data.height/5)*4,
                                window=gorskiicanvas.data.aReadyB)

def realignScreen():
    #screen shown when user wants to create negatives and then realign
    #them to create the gorskii effect
    
    #deletes buttons
    gorskiicanvas.data.alignB.destroy()
    gorskiicanvas.data.negativeB.destroy()
    gorskiicanvas.data.realignB.destroy()

    #buttons for gorskii option screen
    buttonFont = gorskiicanvas.data.buttonFont
    gorskiicanvas.data.aOpenB = tk.Button(gorskiicanvas,
                                           text='Browse for photo!',
                                          command=gorskiiopenPath,
                                          font=buttonFont)
    gorskiicanvas.data.aSaveB = tk.Button(gorskiicanvas,
                                          text='Browse for save path!',
                                         command=gorskiisavePath,
                                         font=buttonFont)
    gorskiicanvas.data.aReadyB = tk.Button(gorskiicanvas,
                                           text='Ready!',
                                           command=wrapperMakeShiftedStrip,
                                           font=buttonFont)

    #text and background image
    gorskiicanvas.create_image(0,0,image=gorskiicanvas.data.background,
                               anchor='nw')

    titleFont = gorskiicanvas.data.titleFont
    gorskiicanvas.create_text(gorskiicanvas.data.width/2,
                              (gorskiicanvas.data.height/5)+5,
                              text='Fig.',font=titleFont,
                              fill='navy')

    title2Font = gorskiicanvas.data.title2Font
    gorskiicanvas.create_text(gorskiicanvas.data.width/2,
                              int((gorskiicanvas.data.height/5)*1.5),
                              text='Prokudin-Gorskii\'s Negatives',
                              font=title2Font,fill='navy')

    title3Font = gorskiicanvas.data.title3Font
    gorskiicanvas.create_text(gorskiicanvas.data.width/2,
                              (gorskiicanvas.data.height/5)*2,
                              text='Create negatives and realign!',
                              font=title3Font,fill='navy')
    
    
    #creates buttons
    gorskiicanvas.create_window(gorskiicanvas.data.width/2,
                                (gorskiicanvas.data.height/5)*3,
                                window=gorskiicanvas.data.aOpenB)
    gorskiicanvas.create_window(gorskiicanvas.data.width/2,
                                int((gorskiicanvas.data.height/5)*3.5),
                                window=gorskiicanvas.data.aSaveB)
    gorskiicanvas.create_window(gorskiicanvas.data.width/2,
                                (gorskiicanvas.data.height/5)*4,
                                window=gorskiicanvas.data.aReadyB)

def gorskiiWindow():
    #window for all gorskii filters,negatives,etc.
    
    global gorskiicanvas

    #create the canvas
    gWindow = tk.Toplevel()
    background = ImageTk.PhotoImage(file='gorskiibackground-2.jpg')
    gWindow.geometry('%dx%d' % (background.width(),background.height()))
    gorskiicanvas = tk.Canvas(gWindow,width=background.width(),
                              height=background.height())

    gWindow.resizable(0,0) #locked, not resizeable

    #set up canvas data
    class Struct: pass
    gorskiicanvas.data = Struct()

    gorskiicanvas.data.background = background
    gorskiicanvas.data.width = background.width()
    gorskiicanvas.data.height = background.height()
    gorskiicanvas.data.titleFont = tkFont.Font(family='Baskerville Old Face',
                                               size=50)
    gorskiicanvas.data.title2Font = tkFont.Font(family='American Typewriter',
                                                size=40,weight=tkFont.BOLD)
    gorskiicanvas.data.title3Font = tkFont.Font(family='American Typewriter',
                                                size=35)
    gorskiicanvas.data.buttonFont = tkFont.Font(family='Noteworthy',
                                                size=15,weight=tkFont.BOLD)

    #draw screen
    gorskiiScreen()

    gorskiicanvas.pack()

    gWindow.mainloop()

def openPath():
    #finds the filepath of the image
    
    filtercanvas.data.filename = tkFileDialog.askopenfilename()

def savePath():
    #finds the path of the folder image is to be saved in
    
    filtercanvas.data.foldername = tkFileDialog.askdirectory()

def filterScreen():
    #screen shown with all the options of filters for the user

    #buttons for filter option screen
    buttonFont = filtercanvas.data.buttonFont
    filtercanvas.data.sepiaB = tk.Button(filtercanvas,
                                         text='Sepia my image!',
                                         command=sepiaScreen,
                                         font=buttonFont)
    filtercanvas.data.greyscaleB = tk.Button(filtercanvas,
                                             text='Greyscale my image!',
                                             command=greyscaleScreen,
                                             font=buttonFont)
    filtercanvas.data.tileB = tk.Button(filtercanvas,
                                        text='Tile my image!',
                                        command=tileScreen,
                                        font=buttonFont)
    filtercanvas.data.technicolorB = tk.Button(filtercanvas,
                                               text='Technicolor my image!',
                                               command=technicolorScreen,
                                               font=buttonFont)
    filtercanvas.data.blurB = tk.Button(filtercanvas,
                                        text='Blur my image!',
                                        command=blurScreen,
                                        font=buttonFont)
    filtercanvas.data.sharpenB = tk.Button(filtercanvas,
                                           text='Sharpen my image!',
                                           command=sharpenScreen,
                                           font=buttonFont)
    filtercanvas.data.pencilB = tk.Button(filtercanvas,
                                          text='Pencil my image!',
                                          command=pencilScreen,
                                          font=buttonFont)
    filtercanvas.data.contrastB = tk.Button(filtercanvas,
                                            text='Contrast my image!',
                                            command=contrastScreen,
                                            font=buttonFont)

    #text and background image
    filtercanvas.create_image(0,0,image=filtercanvas.data.background,
                              anchor='nw')

    titleFont = filtercanvas.data.titleFont
    filtercanvas.create_text(filtercanvas.data.width/2,
                             (filtercanvas.data.height/9),
                             text='Fig.',font=titleFont,
                             fill='navy')

    title2Font = filtercanvas.data.title2Font
    filtercanvas.create_text(filtercanvas.data.width/2,
                             (filtercanvas.data.height/9)+50,
                             text='I\'d like to filter my photo!',
                             font=title2Font,fill='navy')

    #creates buttons
    filtercanvas.create_window(filtercanvas.data.width/4,
                                int((filtercanvas.data.height/6)*3),
                                 window=filtercanvas.data.sepiaB)
    filtercanvas.create_window(filtercanvas.data.width/4,
                                int((filtercanvas.data.height/6)*3.5),
                                 window=filtercanvas.data.greyscaleB)
    filtercanvas.create_window(filtercanvas.data.width/4,
                                (filtercanvas.data.height/6)*4,
                                 window=filtercanvas.data.tileB)
    filtercanvas.create_window(filtercanvas.data.width/4,
                                int((filtercanvas.data.height/6)*4.5),
                                 window=filtercanvas.data.technicolorB)
    filtercanvas.create_window((filtercanvas.data.width/4)*3,
                                (filtercanvas.data.height/6)*3,
                                 window=filtercanvas.data.blurB)
    filtercanvas.create_window((filtercanvas.data.width/4)*3,
                                int((filtercanvas.data.height/6)*3.5),
                                 window=filtercanvas.data.sharpenB)
    filtercanvas.create_window((filtercanvas.data.width/4)*3,
                                (filtercanvas.data.height/6)*4,
                                 window=filtercanvas.data.pencilB)
    filtercanvas.create_window((filtercanvas.data.width/4)*3,
                              int((filtercanvas.data.height/6)*4.5),
                              window=filtercanvas.data.contrastB)

def sepiaScreen():
    #screen shown when user chooses the sepia option for filter
    
    #deletes buttons
    filtercanvas.data.sepiaB.destroy()
    filtercanvas.data.greyscaleB.destroy()
    filtercanvas.data.tileB.destroy()
    filtercanvas.data.technicolorB.destroy()
    filtercanvas.data.blurB.destroy()
    filtercanvas.data.sharpenB.destroy()
    filtercanvas.data.pencilB.destroy()
    filtercanvas.data.contrastB.destroy()

    #buttons for filter option screen
    buttonFont = filtercanvas.data.buttonFont
    filtercanvas.data.aOpenB = tk.Button(filtercanvas,
                                           text='Browse for photo!',
                                          command=openPath,
                                          font=buttonFont)
    filtercanvas.data.aSaveB = tk.Button(filtercanvas,
                                          text='Browse for save path!',
                                         command=savePath,
                                         font=buttonFont)
    filtercanvas.data.aReadyB = tk.Button(filtercanvas,
                                           text='Ready!',
                                           command=wrapperSepia,
                                           font=buttonFont)

    #text and background image
    filtercanvas.create_image(0,0,image=filtercanvas.data.background,
                              anchor='nw')

    titleFont = filtercanvas.data.titleFont
    filtercanvas.create_text(filtercanvas.data.width/2,
                             (filtercanvas.data.height/15)+5,
                             text='Fig.',font=titleFont,
                             fill='navy')

    title2Font = filtercanvas.data.title2Font
    filtercanvas.create_text(filtercanvas.data.width/2,
                             int((filtercanvas.data.height/15)+60),
                             text='Filter my photo!',
                             font=title2Font,fill='navy')

    title3Font = filtercanvas.data.title3Font
    filtercanvas.create_text(filtercanvas.data.width/2,
                             (filtercanvas.data.height/15)+90,
                             text='Sepia my image!',
                             font=title3Font,fill='navy')
    
    
    #creates buttons
    filtercanvas.create_window(filtercanvas.data.width/2,
                               (filtercanvas.data.height/5)*3,
                               window=filtercanvas.data.aOpenB)
    filtercanvas.create_window(filtercanvas.data.width/2,
                               int((filtercanvas.data.height/5)*3.5),
                               window=filtercanvas.data.aSaveB)
    filtercanvas.create_window(filtercanvas.data.width/2,
                               (filtercanvas.data.height/5)*4,
                               window=filtercanvas.data.aReadyB)

def greyscaleScreen():
    #screen shown when user chooses greyscale option for filter
    
    #deletes buttons
    filtercanvas.data.sepiaB.destroy()
    filtercanvas.data.greyscaleB.destroy()
    filtercanvas.data.tileB.destroy()
    filtercanvas.data.technicolorB.destroy()
    filtercanvas.data.blurB.destroy()
    filtercanvas.data.sharpenB.destroy()
    filtercanvas.data.pencilB.destroy()
    filtercanvas.data.contrastB.destroy()

    #buttons for filter option screen
    buttonFont = filtercanvas.data.buttonFont
    filtercanvas.data.aOpenB = tk.Button(filtercanvas,
                                         text='Browse for photo!',
                                         command=openPath,
                                         font=buttonFont)
    filtercanvas.data.aSaveB = tk.Button(filtercanvas,
                                         text='Browse for save path!',
                                         command=savePath,
                                         font=buttonFont)
    filtercanvas.data.aReadyB = tk.Button(filtercanvas,
                                          text='Ready!',
                                          command=wrapperGreyscale,
                                          font=buttonFont)

    #text and background image
    filtercanvas.create_image(0,0,image=filtercanvas.data.background,
                              anchor='nw')

    titleFont = filtercanvas.data.titleFont
    filtercanvas.create_text(filtercanvas.data.width/2,
                             (filtercanvas.data.height/15)+5,
                             text='Fig.',font=titleFont,
                             fill='navy')

    title2Font = filtercanvas.data.title2Font    
    filtercanvas.create_text(filtercanvas.data.width/2,
                             int((filtercanvas.data.height/15)+60),
                             text='Filter my photo!',
                             font=title2Font,fill='navy')

    title3Font = filtercanvas.data.title3Font
    filtercanvas.create_text(filtercanvas.data.width/2,
                             (filtercanvas.data.height/15)+90,
                             text='Greyscale my image!',
                             font=title3Font,fill='navy')
    
    
    #creates buttons
    filtercanvas.create_window(filtercanvas.data.width/2,
                                (filtercanvas.data.height/5)*3,
                                 window=filtercanvas.data.aOpenB)
    filtercanvas.create_window(filtercanvas.data.width/2,
                                int((filtercanvas.data.height/5)*3.5),
                                 window=filtercanvas.data.aSaveB)
    filtercanvas.create_window(filtercanvas.data.width/2,
                                (filtercanvas.data.height/5)*4,
                                 window=filtercanvas.data.aReadyB)

def inputDimensions():
    #input dimensions for tiled filter (rows and cols)

    #asks for rows
    message = 'Enter number of rows in number form'
    title = 'Rows'
    tileRows = tkSimpleDialog.askstring(title,message)

    #asks for cols
    message2 = 'Enter number of columns in number form'
    title2 = 'Columns'
    tileColumns = tkSimpleDialog.askstring(title2,message2)

    #changes the strings to int
    try:
        filtercanvas.data.tileRows = int(tileRows)
        filtercanvas.data.tileCols = int(tileColumns)
        
    except:

        message = "You did not enter a number for either rows or columns!"
        title = "Invalid input!"
        tkMessageBox.showerror(title, message)

def tileScreen():
    #screen shown when user chooses tile option for filter
    
    #deletes buttons
    filtercanvas.data.sepiaB.destroy()
    filtercanvas.data.greyscaleB.destroy()
    filtercanvas.data.tileB.destroy()
    filtercanvas.data.technicolorB.destroy()
    filtercanvas.data.blurB.destroy()
    filtercanvas.data.sharpenB.destroy()
    filtercanvas.data.pencilB.destroy()
    filtercanvas.data.contrastB.destroy()

    #buttons for filter option screen
    buttonFont = filtercanvas.data.buttonFont
    filtercanvas.data.aOpenB = tk.Button(filtercanvas,
                                         text='Browse for photo!',
                                         command=openPath,
                                         font=buttonFont)
    filtercanvas.data.aSaveB = tk.Button(filtercanvas,
                                         text='Browse for save path!',
                                         command=savePath,
                                         font=buttonFont)
    filtercanvas.data.aDimensionsB = tk.Button(filtercanvas,
                                               text='Enter dimensions!',
                                               command=inputDimensions,
                                               font=buttonFont)
    filtercanvas.data.aReadyB = tk.Button(filtercanvas,
                                          text='Ready!',
                                          command=wrapperTiled,
                                          font=buttonFont)

    #text and background image
    filtercanvas.create_image(0,0,image=filtercanvas.data.background,
                              anchor='nw')

    titleFont = filtercanvas.data.titleFont
    filtercanvas.create_text(filtercanvas.data.width/2,
                             (filtercanvas.data.height/15)+5,
                             text='Fig.',font=titleFont,
                             fill='navy')

    title2Font = filtercanvas.data.title2Font
    filtercanvas.create_text(filtercanvas.data.width/2,
                             int((filtercanvas.data.height/15)+60),
                             text='Filter my photo!',
                             font=title2Font,fill='navy')

    title3Font = filtercanvas.data.title3Font
    filtercanvas.create_text(filtercanvas.data.width/2,
                             (filtercanvas.data.height/15)+90,
                             text='Tile my image!',
                             font=title3Font,fill='navy')
    
    
    #creates buttons
    filtercanvas.create_window(filtercanvas.data.width/2,
                               (filtercanvas.data.height/5)*3,
                               window=filtercanvas.data.aOpenB)
    filtercanvas.create_window(filtercanvas.data.width/2,
                               int((filtercanvas.data.height/5)*3.5),
                               window=filtercanvas.data.aSaveB)
    filtercanvas.create_window(filtercanvas.data.width/2,
                               (filtercanvas.data.height/5)*4,
                               window=filtercanvas.data.aDimensionsB)
    filtercanvas.create_window(filtercanvas.data.width/2,
                               int((filtercanvas.data.height/5)*4.5),
                               window=filtercanvas.data.aReadyB)

def technicolorScreen():
    #screen shows when user chooses technicolor option for filter
    
    #deletes buttons
    filtercanvas.data.sepiaB.destroy()
    filtercanvas.data.greyscaleB.destroy()
    filtercanvas.data.tileB.destroy()
    filtercanvas.data.technicolorB.destroy()
    filtercanvas.data.blurB.destroy()
    filtercanvas.data.sharpenB.destroy()
    filtercanvas.data.pencilB.destroy()
    filtercanvas.data.contrastB.destroy()

    #buttons for filter option screen
    buttonFont = filtercanvas.data.buttonFont
    filtercanvas.data.aOpenB = tk.Button(filtercanvas,
                                           text='Browse for photo!',
                                          command=openPath,
                                          font=buttonFont)
    filtercanvas.data.aSaveB = tk.Button(filtercanvas,
                                          text='Browse for save path!',
                                         command=savePath,
                                         font=buttonFont)
    filtercanvas.data.aReadyB = tk.Button(filtercanvas,
                                           text='Ready!',
                                           command=wrapperTechnicolor,
                                           font=buttonFont)

    #text and background image
    filtercanvas.create_image(0,0,image=filtercanvas.data.background,
                              anchor='nw')

    titleFont = filtercanvas.data.titleFont
    filtercanvas.create_text(filtercanvas.data.width/2,
                             (filtercanvas.data.height/15)+5,
                             text='Fig.',font=titleFont,
                             fill='navy')

    title2Font = filtercanvas.data.title2Font
    filtercanvas.create_text(filtercanvas.data.width/2,
                             int((filtercanvas.data.height/15)+60),
                             text='Filter my photo!',
                             font=title2Font,fill='navy')

    title3Font = filtercanvas.data.title3Font
    filtercanvas.create_text(filtercanvas.data.width/2,
                             (filtercanvas.data.height/15)+90,
                             text='Technicolor my image!',
                             font=title3Font,fill='navy')
    
    
    #creates buttons
    filtercanvas.create_window(filtercanvas.data.width/2,
                               (filtercanvas.data.height/5)*3,
                               window=filtercanvas.data.aOpenB)
    filtercanvas.create_window(filtercanvas.data.width/2,
                               int((filtercanvas.data.height/5)*3.5),
                               window=filtercanvas.data.aSaveB)
    filtercanvas.create_window(filtercanvas.data.width/2,
                               (filtercanvas.data.height/5)*4,
                               window=filtercanvas.data.aReadyB)

def blurScreen():
    #screen shows when user choosed blur option for filter
    
    #deletes buttons
    filtercanvas.data.sepiaB.destroy()
    filtercanvas.data.greyscaleB.destroy()
    filtercanvas.data.tileB.destroy()
    filtercanvas.data.technicolorB.destroy()
    filtercanvas.data.blurB.destroy()
    filtercanvas.data.sharpenB.destroy()
    filtercanvas.data.pencilB.destroy()
    filtercanvas.data.contrastB.destroy()

    #buttons for filter option screen
    buttonFont = filtercanvas.data.buttonFont
    filtercanvas.data.aOpenB = tk.Button(filtercanvas,
                                         text='Browse for photo!',
                                         command=openPath,
                                         font=buttonFont)
    filtercanvas.data.aSaveB = tk.Button(filtercanvas,
                                         text='Browse for save path!',
                                         command=savePath,
                                         font=buttonFont)
    filtercanvas.data.aReadyB = tk.Button(filtercanvas,
                                          text='Ready!',
                                          command=wrapperBlur,
                                          font=buttonFont)

    #text and background image
    filtercanvas.create_image(0,0,image=filtercanvas.data.background,
                              anchor='nw')

    titleFont = filtercanvas.data.titleFont
    filtercanvas.create_text(filtercanvas.data.width/2,
                             (filtercanvas.data.height/15)+5,
                             text='Fig.',font=titleFont,
                             fill='navy')

    title2Font = filtercanvas.data.title2Font
    filtercanvas.create_text(filtercanvas.data.width/2,
                             int((filtercanvas.data.height/15)+60),
                             text='Filter my photo!',
                             font=title2Font,fill='navy')

    title3Font = filtercanvas.data.title3Font
    filtercanvas.create_text(filtercanvas.data.width/2,
                             (filtercanvas.data.height/15)+90,
                             text='Blur my image!',
                             font=title3Font,fill='navy')
    
    
    #creates buttons
    filtercanvas.create_window(filtercanvas.data.width/2,
                               (filtercanvas.data.height/5)*3,
                               window=filtercanvas.data.aOpenB)
    filtercanvas.create_window(filtercanvas.data.width/2,
                               int((filtercanvas.data.height/5)*3.5),
                               window=filtercanvas.data.aSaveB)
    filtercanvas.create_window(filtercanvas.data.width/2,
                               (filtercanvas.data.height/5)*4,
                               window=filtercanvas.data.aReadyB)

def sharpenScreen():
    #screen shows when user chooses sharpen option for filter
    
    #deletes buttons
    filtercanvas.data.sepiaB.destroy()
    filtercanvas.data.greyscaleB.destroy()
    filtercanvas.data.tileB.destroy()
    filtercanvas.data.technicolorB.destroy()
    filtercanvas.data.blurB.destroy()
    filtercanvas.data.sharpenB.destroy()
    filtercanvas.data.pencilB.destroy()
    filtercanvas.data.contrastB.destroy()

    #buttons for filter option screen
    buttonFont = filtercanvas.data.buttonFont
    filtercanvas.data.aOpenB = tk.Button(filtercanvas,
                                         text='Browse for photo!',
                                         command=openPath,
                                         font=buttonFont)
    filtercanvas.data.aSaveB = tk.Button(filtercanvas,
                                         text='Browse for save path!',
                                         command=savePath,
                                         font=buttonFont)
    filtercanvas.data.aReadyB = tk.Button(filtercanvas,
                                          text='Ready!',
                                          command=wrapperSharpen,
                                          font=buttonFont)

    #text and background image
    filtercanvas.create_image(0,0,image=filtercanvas.data.background,
                              anchor='nw')


    titleFont = filtercanvas.data.titleFont
    filtercanvas.create_text(filtercanvas.data.width/2,
                             (filtercanvas.data.height/15)+5,
                             text='Fig.',font=titleFont,fill='navy')

    title2Font = filtercanvas.data.title2Font
    filtercanvas.create_text(filtercanvas.data.width/2,
                             int((filtercanvas.data.height/15)+60),
                             text='Filter my photo!',
                             font=title2Font,fill='navy')

    title3Font = filtercanvas.data.title3Font
    filtercanvas.create_text(filtercanvas.data.width/2,
                             (filtercanvas.data.height/15)+90,
                             text='Sharpen my image!',
                             font=title3Font,fill='navy')
    
    
    #creates buttons
    filtercanvas.create_window(filtercanvas.data.width/2,
                               (filtercanvas.data.height/5)*3,
                               window=filtercanvas.data.aOpenB)
    filtercanvas.create_window(filtercanvas.data.width/2,
                               int((filtercanvas.data.height/5)*3.5),
                               window=filtercanvas.data.aSaveB)
    filtercanvas.create_window(filtercanvas.data.width/2,
                               (filtercanvas.data.height/5)*4,
                               window=filtercanvas.data.aReadyB)

def pencilScreen():
    #screen shows when user chooses pencil option for filter
    
    #deletes buttons
    filtercanvas.data.sepiaB.destroy()
    filtercanvas.data.greyscaleB.destroy()
    filtercanvas.data.tileB.destroy()
    filtercanvas.data.technicolorB.destroy()
    filtercanvas.data.blurB.destroy()
    filtercanvas.data.sharpenB.destroy()
    filtercanvas.data.pencilB.destroy()
    filtercanvas.data.contrastB.destroy()

    #buttons for filter option screen
    buttonFont = filtercanvas.data.buttonFont
    filtercanvas.data.aOpenB = tk.Button(filtercanvas,
                                         text='Browse for photo!',
                                         command=openPath,
                                         font=buttonFont)
    filtercanvas.data.aSaveB = tk.Button(filtercanvas,
                                         text='Browse for save path!',
                                         command=savePath,
                                         font=buttonFont)
    filtercanvas.data.aReadyB = tk.Button(filtercanvas,
                                          text='Ready!',
                                          command=wrapperPencil,
                                          font=buttonFont)

    #text and background image
    filtercanvas.create_image(0,0,image=filtercanvas.data.background,
                              anchor='nw')

    titleFont = filtercanvas.data.titleFont
    filtercanvas.create_text(filtercanvas.data.width/2,
                             (filtercanvas.data.height/15)+5,
                             text='Fig.',font=titleFont,fill='navy')

    title2Font = filtercanvas.data.title2Font
    filtercanvas.create_text(filtercanvas.data.width/2,
                             int((filtercanvas.data.height/15)+60),
                             text='Filter my photo!',
                             font=title2Font,fill='navy')

    title3Font = filtercanvas.data.title3Font
    filtercanvas.create_text(filtercanvas.data.width/2,
                             (filtercanvas.data.height/15)+90,
                             text='Pencil my image!',
                             font=title3Font,fill='navy')
    
    
    #creates buttons
    filtercanvas.create_window(filtercanvas.data.width/2,
                               (filtercanvas.data.height/5)*3,
                               window=filtercanvas.data.aOpenB)
    filtercanvas.create_window(filtercanvas.data.width/2,
                               int((filtercanvas.data.height/5)*3.5),
                               window=filtercanvas.data.aSaveB)
    filtercanvas.create_window(filtercanvas.data.width/2,
                               (filtercanvas.data.height/5)*4,
                               window=filtercanvas.data.aReadyB)

def contrastScreen():
    #screen shows when user chooses contrast option for filter
    
    #deletes buttons
    filtercanvas.data.sepiaB.destroy()
    filtercanvas.data.greyscaleB.destroy()
    filtercanvas.data.tileB.destroy()
    filtercanvas.data.technicolorB.destroy()
    filtercanvas.data.blurB.destroy()
    filtercanvas.data.sharpenB.destroy()
    filtercanvas.data.pencilB.destroy()
    filtercanvas.data.contrastB.destroy()

    #buttons for filter option screen
    buttonFont = filtercanvas.data.buttonFont
    filtercanvas.data.aOpenB = tk.Button(filtercanvas,
                                         text='Browse for photo!',
                                         command=openPath,
                                         font=buttonFont)
    filtercanvas.data.aSaveB = tk.Button(filtercanvas,
                                         text='Browse for save path!',
                                         command=savePath,
                                         font=buttonFont)
    filtercanvas.data.aReadyB = tk.Button(filtercanvas,
                                          text='Ready!',
                                          command=wrapperContrast,
                                          font=buttonFont)

    #text and background image
    filtercanvas.create_image(0,0,image=filtercanvas.data.background,
                              anchor='nw')


    titleFont = filtercanvas.data.titleFont
    filtercanvas.create_text(filtercanvas.data.width/2,
                             (filtercanvas.data.height/15)+5,
                             text='Fig.',font=titleFont,
                             fill='navy')

    title2Font = filtercanvas.data.title2Font
    filtercanvas.create_text(filtercanvas.data.width/2,
                             int((filtercanvas.data.height/15)+60),
                             text='Filter my photo!',
                             font=title2Font,fill='navy')

    title3Font = filtercanvas.data.title3Font
    filtercanvas.create_text(filtercanvas.data.width/2,
                             (filtercanvas.data.height/15)+90,
                             text='Contrast my image!',
                             font=title3Font,fill='navy')
    
    
    #creates buttons
    filtercanvas.create_window(filtercanvas.data.width/2,
                               (filtercanvas.data.height/5)*3,
                               window=filtercanvas.data.aOpenB)
    filtercanvas.create_window(filtercanvas.data.width/2,
                               int((filtercanvas.data.height/5)*3.5),
                               window=filtercanvas.data.aSaveB)
    filtercanvas.create_window(filtercanvas.data.width/2,
                               (filtercanvas.data.height/5)*4,
                               window=filtercanvas.data.aReadyB)

def filterWindow():
    #options separate window with a list of all the different filters
    #offered
    
    #window for all filters
    global filtercanvas

    #create the canvas
    fWindow = tk.Toplevel()
    background = ImageTk.PhotoImage(file='filterbackground.jpg')
    fWindow.geometry('%dx%d' % (background.width(),background.height()))
    filtercanvas = tk.Canvas(fWindow,width=background.width(),
                             height=background.height())

    fWindow.resizable(0,0) #lock, cannot be resized

    #set up canvas data
    class Struct: pass
    filtercanvas.data = Struct()

    filtercanvas.data.background = background
    filtercanvas.data.width = background.width()
    filtercanvas.data.height = background.height()
    filtercanvas.data.titleFont = tkFont.Font(family='Baskerville Old Face',
                                              size=45)
    filtercanvas.data.title2Font = tkFont.Font(family='American Typewriter',
                                               size=35,weight=tkFont.BOLD)
    filtercanvas.data.title3Font = tkFont.Font(family='American Typewriter',
                                              size=30)
    filtercanvas.data.buttonFont = tkFont.Font(family='Noteworthy',
                                               size=15,weight=tkFont.BOLD)

    #draw screen
    filterScreen()

    filtercanvas.pack()

    fWindow.mainloop()

def splashWindow():
    #window for splash screen and option screen
    #this is the main window!

    try:
        global splashcanvas
        
        # create the canvas
        root=tk.Tk()
        background = ImageTk.PhotoImage(file='splashscreen.jpg')
        splashcanvas = tk.Canvas(root,width=background.width(),
                                 height=background.height())

        root.resizable(0,0) #locked, cannot be resized
        
        # Set up canvas data 
        class Struct: pass
        splashcanvas.data = Struct()
        
        splashcanvas.data.topbackground = background
        splashcanvas.data.width = background.width()
        splashcanvas.data.height = background.height()
        splashcanvas.data.root = root
        splashcanvas.data.titleFont = tkFont.Font(family='Baskerville Old Face',
                                                  size=50)
        splashcanvas.data.title2Font = tkFont.Font(family='American Typewriter',
                                                   size=40,weight=tkFont.BOLD)
        splashcanvas.data.buttonFont = tkFont.Font(family='Noteworthy',
                                                   size=15,weight=tkFont.BOLD)
        
        #draw screen
        splashScreen()

        splashcanvas.pack()

        # and launch the app
        root.mainloop()

    except: #user pressed X instead of quit

        quitNow()

splashWindow()

