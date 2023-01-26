# lm_digital_ad_renderer

## To compile .exe file execute this command:
```commandline
pyinstaller '.\LM AD Render.py' --icon .\assets\photo_2021-05-11_11-55-45.ico --onefile 
```

## To run compiled .exe you will need to:
1. Install ffmpeg and add "bin" folder in PATH environment variable
2. Install imagemagick and add "ImageMagick" folder in PATH environment variable


## What this program can do:
1. Render videos based on directory containing other directories with this structure:

_Root directory name: Image size
Inside of root directory directories (JPG, Видео, Исходники)_
Example:
```
720x360 -
	 |
	  - Исходники -
	 |             |
	 |              - Illustrator 2020.ai
	  - JPG -
	 |       |
	 |        - 720x360.jpg
	  - Видео
```
2. Render and catoligize videos based on directory containing .jpg & .ai files
3. Render .tif files based on directory containing other directories with this structure:

_Root directory name: Image size
Inside of root directory are directories (Принт, Исходники)_
Example:
```
1200x1800 -
	   |
	    - Исходники - 
	   |             |
	   |              - Illustrator 2020.ai
	   |              - Illustrator 2020.eps
	   |
	    - Принт
```