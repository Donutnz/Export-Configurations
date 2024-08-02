from steputils import p21

fileName="TMC_RPWCMP15V"

stepFile=p21.readfile(fileName+".step")
sData:p21.DataSection=stepFile.data[0]

# Set Headers
headerAuthor=("JOSH T-B",)
headerOrg=("THE METAL COMPANY",)
headerAuth="S. FISHER & SONS LTD."

fHeader=stepFile.header.get("FILE_NAME")

if(fHeader is not None):
    fileNameInfo=[
        fHeader.params[0], #Name
        fHeader.params[1], #Timestamp
        headerAuthor, #Author
        headerOrg, #Organization
        fHeader.params[4], #Preprocessor version
        fHeader.params[5], #Originating System
        headerAuth #Authorization
        ]
    newFName=p21.entity("FILE_NAME", fileNameInfo)
    stepFile.header.add(newFName)

# Replace PRODUCT name
for k,v in sData.instances.items():
    if isinstance(v, p21.SimpleEntityInstance):
        #print(str(k)+":"+str(v.entity.name))
        if v.entity.name == "PRODUCT" or v.entity.name == "PRODUCT_DEFINITION":
            if(v.entity.params[0] == fileName):
                swpParams:list=list(v.entity.params)
                swpParams[1]=v.entity.params[0]
                repEntity=p21.simple_instance(v.ref, v.entity.name, swpParams)
                sData.add(repEntity)

stepFile.save("test.step")
