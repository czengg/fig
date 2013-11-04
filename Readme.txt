{\rtf1\ansi\ansicpg1252\cocoartf1138\cocoasubrtf320
{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
\margl1440\margr1440\vieww13860\viewh8400\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural

\f0\fs24 \cf0 Project description:\
\
modules used:\
Tkinter\
PIL\
random\
copy\
\
install PIL: http://www.pythonware.com/products/pil/\
		download the latest version of PIL\
\
if Mac: use homebrew\
	then:\
		brew install pil\
\pard\pardeftab720
\cf0 		ln -s /usr/local/Cellar/pil/1.1.7/lib/python2.7/site-packages/PIL /Library/Python/2.7/site-packages/PIL\
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural
\cf0 \
fonts -- copy and paste the fonts in fonts file to /Library/Fonts (for mac)\
					or equivalent fonts folder for pc\
\
\
Project is split into three separate part:\
\
Prudin-Gorskii's Negatives\
Filtering Images\
Fig.let program for filtering\
\
\
Prudin-Gorskii's Negatives:\
\
Background:\
	A method of color rendering that was developed in Russia in the 1900s. Before the color photography, Prokudin-Gorskii developed this technique in which he took three photos of the same image, but using different colored filters (red,green,blue). He then took these 'black and white' images essentially now held red, green, blue values of the 'image' and displayed them atop each other to create a colored image.\
\
My Project:\
\
	For my project, I give the user the option to align their preexisting Prokudin-Gorskii negative, generate their own Prokudin-Gorskii negative using a colored image of their own, or using an image of their own, generate a shifted Prokudin-Gorskii negative that would be realigned, creating the effect of an aligned Prokudin-Gorskii image.\
\
Filtering images:\
\
	Users have the option of filtering their own image as a whole. There are eight options in total: Sepia, Greyscale, Tile, Technicolor, Blur, Sharpen, Pencil, Contrast.\
\
Sepia - gives the image a sepia tint. Image lights and darks may also be enhanced in the process.\
Greyscale - makes the image black and white.\
Tile - user inputs how many rows and columns they want and program gives an image that has the \
	input image rows*cols times with that many rows and that many cols\
Technicolor - makes an image 2x2 that is like tile but each tile has a different color\
Blur - makes the image blurry\
Sharpen - sharpens the image\
Pencil - makes it look as if the image was drawn using different weighted/dark-intensity pencils\
Contrast - makes image lights and darks intensified\
\
Fig.let:\
\
	Users have the option to edit their own image in parts with different filters. Running like a paint program, the user is given five check buttons at the top. Only one check button can be checked at a time. Each button represents a different filter that can be used. The checked filter will be used at the given region that the user wishes within the scope of the image. \
\
First a rectangle will appear in which the user will be able to apply the filter. Then when the user releases the mouse click the rectangle will disappear and the filter will be applied. If the user wants to put two filters at the same location, double click the second button instead of drawing a new rectangle. When the user is satisfied with the picture, they can click done which will save the edited image.\
\
}