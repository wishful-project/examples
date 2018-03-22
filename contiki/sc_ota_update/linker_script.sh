ELF_PROGRAM_FILE_NAME=$1
FIRMWARE=$2
INIT_FUNCTION=$3

echo "Will link $ELF_PROGRAM_FILE_NAME with $FIRMWARE" 

IFS_old=$IFS
IFS=$'\n'
UNDEFINED_SYMBOLS=(`nm ${1}.merged | grep ' U '`)
IFS=$IFS_old

echo "" > $ELF_PROGRAM_FILE_NAME.lds

for UNDEFINED_SYMBOL in "${UNDEFINED_SYMBOLS[@]}"
do
    UNDEFINED_SYMBOL_ARRAY=(${UNDEFINED_SYMBOL})
    UNDEFINED_SYMBOL_ADDR=`nm $FIRMWARE | grep " ${UNDEFINED_SYMBOL_ARRAY[1]}"$ | awk '{print $1;}'`
    echo "PROVIDE(\"${UNDEFINED_SYMBOL_ARRAY[1]}\"=0x${UNDEFINED_SYMBOL_ADDR});" >> $ELF_PROGRAM_FILE_NAME.lds
done

DMM_RAM_ALIGNED_ADDR=`nm $FIRMWARE | grep dmm_ram_aligned | awk '{print $1;}'`
echo "ENTRY($INIT_FUNCTION)
SECTIONS
{
    . = 0x00202074;
    .text : { *(.text*) }
    .rodata : { *(.rodata*) }
    . = 0x$DMM_RAM_ALIGNED_ADDR;
    .data : ALIGN(4) { *(.data*) }
    .bss : ALIGN(4) { *(.bss*) }
}" >> $ELF_PROGRAM_FILE_NAME.lds

arm-none-eabi-gcc -mcpu=cortex-m3 -mthumb -mlittle-endian -fshort-enums -fomit-frame-pointer -fno-strict-aliasing -Wall -Os -x c -P -E $ELF_PROGRAM_FILE_NAME.lds | grep -v '^\s*#\s*pragma\>' > $ELF_PROGRAM_FILE_NAME.ld
arm-none-eabi-ld -nostdlib -nodefaultlibs -nostartfiles -T $ELF_PROGRAM_FILE_NAME.ld -n --sort-section=alignment -cref --no-warn-mismatch $ELF_PROGRAM_FILE_NAME.merged -o $ELF_PROGRAM_FILE_NAME.linked
arm-none-eabi-objcopy -S -R .comment -R .ARM.attributes $ELF_PROGRAM_FILE_NAME.linked $ELF_PROGRAM_FILE_NAME.stripped
