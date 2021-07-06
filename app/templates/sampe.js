var custom_ui_main = function () {
    var element = document.querySelector("#relativeLocation");
    var makeAnnotation = UtilityService.annotationFactory(element, ".annotator-hl");
    var ui = { interactionPoint: null };
    return {start: function start() 
        {ui.highlighter = new annotator.ui.highlighter.Highlighter(element);
            ui.textselector = new annotator.ui.textselector.TextSelector(element, 
                {onSelection: function onSelection(ranges, event) 
                    {if (ranges.length > 0)
                        {annotation = makeAnnotation(ranges);
                        var commentModalPosition = UtilityService.mousePosition(event);
                        // document.getElementById("commentEditContainer").style.display = "block";
                    } }});},destroy: function destroy() 
                    {ui.highlighter.destroy();ui.textselector.destroy();},
                    annotationCreated: function annotationCreated(a)
                     {ui.highlighter.draw(a);},
                     annotationsLoaded: function annotationsLoaded(a) 
                     {ui.highlighter.drawAll(a).then(
                         function () {},
                         annotationDeleted: function annotationDeleted(a)
                          {ui.highlighter.undraw(a);},
                          annotationUpdated: function annotationUpdated(a) {
                              ui.highlighter.redraw(a);}};}