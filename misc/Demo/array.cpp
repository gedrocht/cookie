int foo [5] = { 16, 2, 77, 40, 12071 };

/*

value_address = array_address + index * array_type_size

array_address = 1000
array_type_size = 4 bytes

foo[0] = 1000 + 0 * 4 = 1000
foo[1] = 1000 + 1 * 4 = 1004
foo[2] = 1000 + 2 * 4 = 1008



X = foo[0] = 16
Y = foo[1] = 2
1000: X
1001: X
1002: X
1003: X
1004: Y
1005: Y
1006: Y
1007: Y
1008: Z
1009: Z
1010:



*/