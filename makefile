# mkfile_path := $(abspath $(lastword $(MAKEFILE_LIST)))
# current_dir := $(notdir $(patsubst %/,%,$(dir $(mkfile_path))))
current_dir = $(shell pwd)
cclsFiles := $(shell rm -f ${current_dir}/compile_commands.json & find ${current_dir} -type f -iname "compile_commands.json" | tr "\n" " ")

json:
	jq -s 'flatten' ${cclsFiles} 1> ${current_dir}/compile_commands.json
