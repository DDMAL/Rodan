# Script to add pixel_wrapper functionality code to pixel.js

f = open('./source/js/plugins/pixel.js/source/pixel.js', 'r')
lines = f.readlines()
f.close()

import_flag = True
construct_flag = True
activate_flag = True
deactivate_flag = True

import_code = "import {PixelWrapper} from '../../pixel-wrapper';\n"
construct_code = "\t\tthis.pixelWrapper = null;\n"
activate_code = """\n\t\t// Activate wrapper
\t\tif (this.pixelWrapper === null) 
\t\t\tthis.pixelWrapper = new PixelWrapper(this);
\t\tthis.pixelWrapper.activate();\n"""
deactivate_code = "\t\t// Deactivate wrapper\n\t\tthis.pixelWrapper.deactivate();\n\n"

if import_code in lines:
    print("The wrapper code has already been added!")
    raise SystemExit

f = open('./source/js/plugins/pixel.js/source/pixel.js', 'w')

for i in range(len(lines)):
    if ('import {' in lines[i] and import_flag):
        lines.insert(i, import_code)
        import_flag = False
    if ('constructor' in lines[i] and construct_flag):
        lines.insert(i+2, construct_code)
        construct_flag = False
    if ('new Tutorial();' in lines[i] and activate_flag):
        lines.insert(i+1, activate_code)
        activate_flag = False
    if ('deactivatePlugin ()' in lines[i] and deactivate_flag):
        lines.insert(i+2, deactivate_code)
        deactivate_Flag = False

# Write to file
for i in range(len(lines)):
    f.write(lines[i])

f.close()


# Remove the index.html copying line from pixel.sh, which is incompatible with pixel_wrapper

f = open('./source/js/plugins/pixel.js/pixel.sh', 'r')
lines = f.readlines()
f.close()

f = open('./source/js/plugins/pixel.js/pixel.sh', 'w')
for i in range(len(lines)):
    if ('scp ./index.html ../../../../' in lines[i]):
        lines[i] = '# scp ./index.html ../../../../\n'
    if ('echo "> gulp"' in lines[i]):
        lines[i] = 'echo "> gulp develop:rodan"\n'
        lines[i+1] = 'gulp develop:rodan\n'
    if ('echo "> npm install -g gulp webpack"' in lines[i]):
        lines[i] = 'echo "> npm install -g gulp@4.0.0 webpack"\n'
        lines[i+1] = 'sudo npm install -g gulp@4.0.0 webpack\n'
    f.write(lines[i])

f.close()
