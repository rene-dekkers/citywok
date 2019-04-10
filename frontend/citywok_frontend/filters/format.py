from citywok_frontend.filterloader import FilterModule
@FilterModule()
def byteformat(size_bytes):
	if size_bytes == 1:
		return "1 byte"
	suffixes_table = [('bytes',0),('KB',0),('MB',1),('GB',2),('TB',2), ('PB',2)]
	num = float(size_bytes)
	for suffix, precision in suffixes_table:
		if num < 1024.0: break
		num /= 1024.0

	if precision == 0 or round(num, ndigits=precision).is_integer():
		formatted_size = "%d" % num
	else:
		formatted_size = str(round(num, ndigits=precision))
	return "%s %s" % (formatted_size, suffix)
