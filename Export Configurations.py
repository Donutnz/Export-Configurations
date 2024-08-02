#Author Donutnz
#Description Exports each row of a configuration enabled file as STEP files and then modifies each exported STEP file to work with TMC's naming requirements.

import adsk.core, adsk.fusion, adsk.cam, traceback
from .steputils import p21

# Header Details
headerAuthor=("JOSH T-B",)
headerOrg=("THE METAL COMPANY",)
headerAuth="S. FISHER & SONS LTD."

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface

        design=adsk.fusion.Design.cast(app.activeProduct)

        # Check if this is a configured design.
        if not design.isConfiguredDesign:
            ui.messageBox("Error: The current design is not configured! This script can only run on configured designs.")
            return
        
        # Get Output Folder
        targetFolderPath=""
        folderDlg=ui.createFolderDialog()
        folderDlg.title="Choose Output Folder"

        dlgResult=folderDlg.showDialog()
        if(dlgResult == adsk.core.DialogResults.DialogOK):
            targetFolderPath=folderDlg.folder
        else:
            return

        # Get each configuration
        topTable = design.configurationTopTable
        
        # Export each configuration
        exportMgr=design.exportManager
        filesCnt=0

        app.log("Beginning exporting into {}".format(targetFolderPath))

        for row in topTable.rows:
            app.log("Starting: {}".format(row.name))

            rowActSuccess=row.activate()

            if not rowActSuccess:
                raise Exception("Error activating row: {}".format(row.name))

            fileName=targetFolderPath+'/'+row.name+".step"

            #rootObj=design.activeComponent

            stepExpOpts=exportMgr.createSTEPExportOptions(fileName)
            exportMgr.execute(stepExpOpts)

            app.log("Exported standard step file: {}".format(fileName))

            #Reopen exported STEP file to tweak names and add header stuff.
            try:
                stepFile=p21.readfile(fileName)
                sData:p21.DataSection=stepFile.data[0]
                
                oldHeader=stepFile.header.get("FILE_NAME")

                if(oldHeader is not None):
                    fileNameInfo=[
                        oldHeader.params[0], #Name
                        oldHeader.params[1], #Timestamp
                        headerAuthor, #Author
                        headerOrg, #Organization
                        oldHeader.params[4], #Preprocessor version
                        oldHeader.params[5], #Originating System
                        headerAuth #Authorization
                        ]
                    newFName=p21.entity("FILE_NAME", fileNameInfo)
                    stepFile.header.add(newFName)

                # Replace PRODUCT and PRODUCT_DEFINITION. This makes the root component show up with the TMC preferred name for some CAD programs.
                for k,v in sData.instances.items():
                    if isinstance(v, p21.SimpleEntityInstance):
                        #print(str(k)+":"+str(v.entity.name))
                        if v.entity.name == "PRODUCT" or v.entity.name == "PRODUCT_DEFINITION":
                            if(v.entity.params[0] == row.name):
                                swpParams:list=list(v.entity.params)
                                swpParams[1]=v.entity.params[0]
                                repEntity=p21.simple_instance(v.ref, v.entity.name, swpParams)
                                sData.add(repEntity)

                stepFile.save(fileName)
                app.log("Modified step file: {}".format(fileName))

            except IOError as e:
                app.log("Error opening STEP file: {} with error: {}".format(e.filename, e))
            except p21.ParseError as e:
                app.log("Error parsing STEP file: {} with error: {}".format(e))
            
            app.log("Done: {}\n".format(row.name))
            filesCnt+=1

        ui.messageBox("Operation Complete. "+str(filesCnt)+" Step Files Exported to: "+targetFolderPath+".")

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
