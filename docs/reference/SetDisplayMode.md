## SetDisplayMode ##

```python
fpdf.set_display_mode(zoom, layout: str)
```
### Description ###

Defines the way the document is to be displayed by the viewer. The zoom level can be set: pages can be displayed entirely on screen, occupy the full width of the window, use real size, be scaled by a specific zooming factor or use viewer default (configured in the Preferences menu of Adobe Reader). The page layout can be specified too: single at once, continuous display, two columns or viewer default.

### Parameters ###

zoom:
> The zoom to use. It can be one of the following string values:
>>  * `fullpage`: displays the entire page on screen
>>  * `fullwidth`: uses maximum width of window
>>  * `real`: uses real size (equivalent to 100% zoom)
>>  * `default`: uses viewer default mode
>>  * or a number indicating the zooming factor to use.

layout:
> The page layout. Possible values are:
>>  * `single`: displays one page at once
>>  * `continuous`: displays pages continuously
>>  * `two`: displays two pages on two columns
>>  * `default`: uses viewer default mode
> Default value is `default`.



