def encrypt(key, s): 
    b = bytearray(str(s).encode('utf-8')) 
    n = len(b) # 求出 b 的字节数 
    c = bytearray(n*2) 
    j = 0 
    for i in range(0, n): 
        b1 = b[i] 
        b2 = b1 ^ key # b1 = b2^ key 
        c1 = b2 % 16 
        c2 = b2 // 16 # b2 = c2*16 + c1 
        c1 = c1 + 65 
        c2 = c2 + 65 # c1,c2都是0~15之间的数,加上65就变成了A-P 的字符的编码 
        c[j] = c1 
        c[j+1] = c2 
        j = j+2 
    return c.decode('utf-8') 
 
def decrypt(key, s): 
    c = bytearray(str(s).encode('utf-8')) 
    n = len(c) # 计算 b 的字节数 
    if n % 2 != 0 : 
        return "" 
    n = n // 2 
    b = bytearray(n) 
    j = 0 
    for i in range(0, n): 
        c1 = c[j] 
        c2 = c[j+1] 
        j = j+2 
        c1 = c1 - 65 
        c2 = c2 - 65 
        b2 = c2*16 + c1 
        b1 = b2^ key 
        b[i]= b1 
    return b.decode('utf-8')
