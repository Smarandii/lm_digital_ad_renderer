# lm_digital_ad_renderer

## Tasks for project:

0. Prepare repository
1. Enhance GUI:
    1. Transfer GUI to .ui files
2. Enhance functionality:
    - [x] 1. Work with .tiff files
3. Code review/refactor
    - [x] 2. Add wmv format


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