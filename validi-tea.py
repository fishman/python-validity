
from binascii import hexlify, unhexlify
from struct import pack, unpack

# Emulate the 32bit x86 sar instruction (shift right, arithmetic)
def sar(val, n): 
    mask=0xffffffff << (32-n)
    # signed?
    if val & 0x80000000:
        return (val >> n) | mask
    else:
        return (val >> n) & ~mask

# Textbook TEA implementation (except signed arithmetics is used instead of unsigned, d'oh)
def tea(k, iv):
    k = unpack('<LLLL', k)
    v0, v1 = unpack('<LL', iv)

    summ=0
    for _ in range(0, 0x20):
        summ += 0x9E3779B9
        v0 += (sar(v1, 5) + k[1]) ^ ((v1 << 4) + k[0]) ^ (v1 + summ)
        v1 += (sar(v0, 5) + k[3]) ^ ((v0 << 4) + k[2]) ^ (v0 + summ)

    return pack('<LL', v0 & 0xffffffff, v1 & 0xffffffff)

# Split input in 8 byte blocks
def blocks(i):
    while len(i) > 0:
        yield i[:8]
        i=i[8:]

def xor(a, b):
    return bytearray([x^y for x, y in zip(a, b)])

# CFB mode block cipher on top of TEA
def btea(k, iv, ct, encrypt):
    for block in blocks(ct):
        iv=tea(k, iv)

        out=xor(iv, block)
        yield out

        # Feedback
        if encrypt:
            iv = out
        else:
            iv = block


# Garble the key and hardcode the IV
def validitea(key, ct, encrypt):
    key=xor(key, unhexlify('35096523902564797868805139163491'))
    iv=unhexlify('2365093551806878')
    return btea(key, iv, ct, encrypt)

frags=[
'c82ae3735cc0413709a57170eb14559242bb8bb559f8133b901d0b5f0b28c14c8c72eaba88d45228d56eb5807edc044c6e0551d3575884ac72b83c8013791018b5f39722f71f6eed8362cefa1f92350b3def475df55d08dec481219dbd0b84f5002e4b8a69786ed7fdc80b841611f3bcdfbaba815c736e7779e01f7caf62e3260aa6f4fc8253770beb4b0bf8862035ef58a14ae765c9e4dc7754ad0011ac19ccccea56a0f78da2d66654aaa98d9ceab2f61afba9a69208d385142ff2fc19f16fbcf5b7d918720f97192dcf10bc2b33859d502c60db9409e6d4bcc26e0e0aac63fe646880ce69cb0318b9a9519b4cc4aa7fae97e53b73343ae69e3001c0ed103b2d8afcb4d16559c10959c9d26978aa5c385dde3715870715c83a2f50558d63336984a731e22679bf72a6cb7262cfa588fd5175ca24b68f8e14c1f19da4373a082445ed3da8144764188f11101b42b32604f1b05406707f91c41a0117da82dda4831dff8c205a4853393d3863c1845ee4df9894a78efe92a9bc8a521e747f135708b3e2c2dc5118f785ccaf48c4faa8177788fbe7cae3a1396d58cc7b7535c89053df3a40d5367b8904c5a6b2785397548bd6374ad695ae7e5afb0312b76a41385e0cdd0a31753e05d8e10d895c15abc4f149007ab887b8f151907589d1671c405cf7ba95e9dac44e013be5e6e9',
'c82ae3735cc0413709a57130e6145592ce2b6e020a71f3b24178ae5fc1e531baef269f34645f42fede5c4b17a5f7c80df6b1cf82e9498ea5f78fffa3fedb62cbd6be72b2b4cf09e1493eaa9b3f3f7f60973e46c4f0ba44773ff500dd70e52d22e17de012e4e0638c52def54a606d5109758707cd08e8d6e29c80587a5b7273dc2f427d076386a4ed1dc568569cae4e46eacfc6136f4bf4aa60c1215222ec18cf88093e807562b2d489bfc0b379bd7c312538a5df6f3c5ce2cbc36c00f1c66d0a29ca24619e67e6782cda070b75000b0bebe872a881bd3321635f7392944752878b05c37fda82725aa2169d5aedaafee547c1c3f0d25c0fb510771ad692cac14cdc57b49cc23e2fe57f0fc4047ab51343340a881abc1009d017606f15256cc5550adfa4a25b569b53564e35438e5d97d0017d7f0d534d40c99c2fa7915a025ffe58fbaac7f92873a9eb198cbd43a9d0831a892769b0590530375caaf307c2700ac7c9fe8e915558b2d92d696593831c74c7c44960851cd553c513e5356e96c42742f08862798d6e610dfcbfa06c7aa1e7c391a196af04e558fc372c50d3088de27b3edcbc8a99e758ad71af3d103137f6fc57358e89d48520b20b48adfb655aadd328172013d9578f751655d7d6379feed10aa1656ab08d27e2a11bd977ff7c4f2dac5179e90aaa9f59022d1fe9b151a84bc84917b017d1735a95f7ec202da7664adafee7c1ec53db818bb33e88803c9f1b81b48dfe5a0c4b4bfd837f5ca7e846f728faab7ca6b893e51f6b156978a18e3d0afc26',
'c82ae3735cc0413709a57170eb1455924eb0d3b656f86eb3312b7fa05a6a7a5995233515e89430b3278529f2a4215d615ed1008c9a3f707ee0868ab62a1df7fd90e2bd344e58c6e510973ed3d276ca7a5d4f4ef6f6010c17db76a928d40011f810e42fbae3b278f991e7a228fbe01406692964c4b57b5fd4d633fab39cf79e0984695ee83525ed7a518bf37e354888ae630021dabe7cd3c2fc80a215eb79bf1366879cc69938169fb7af2847352108f4b58679cbb0051cae6933a9b1a0dcddeb0a0c979923ffaafc2bc04e2156c2e73ce9017cc662468f8ef25738a0b168fc600fd687e912dc0a1d30a1280e7baf301a719e0c8b02a7cd52e89e0f814c1d25e094425ec4a0ca6f930d076145617b23af5f92beccd15350fd33982cfcbd7c38cf62866e7789abf09b6860a7053a8bec043e6be405ab12588ec0ac32333724e8072c5c7651a03cd287a2cc1fd5b41d80946447a2d0c8f7c7660113dead200dc19999481e0f6570c0245f5fd1ede5fbf9e2a50e0abd605afdbeaf51487756885c11f0bc18db7004a009aae6b20098ede5b7ddd6290dd431111447b7705eef7344acaf4ea4581bbb14649748f78855ab0fe717b1497b6d9ea863378d22819410566a7fd43123c23489f9dbebf0eb15669400b336796095b697fef935b6651d378362d3435dc5ab93288b4051ce09aa',
'c82ae3735cc0413709a571f0ec145592e6d0cb092e1fcf125ee4428fe0b7a9df85fcc04c009526c4f10bf0fb090e7214f655dbe88032c2ab8217cdd99867f320a9edb40f2be5dc8ee988016aa162acb32e4c94a3550d0264f4b745d386094700027de6164852b954bb3985dcda1a99606f5cef3b1801ef50849d783a9e825205580d2e268191d261fe98743b8bf1b174a55eee5745643d90898af070a32dcfa6d5fd3d1575670d01910fd5e3ba1dfee3123a963c15b63e1f0dbe6c5119c9fab0133a631cd8125f3f1aa5e7cbbf9518de2aaf74e10ab506b619896e4c618b551a0e271d310a63b581a389f003688f54295a6842daaa75c95071133ee8c5140f8d909cc5ee0d596cb0c59e83064d571e919333326d0cdbf7266b0d52e6e9e011ee5d0f9dd60d2df3e863f4d94e1734dbf9260452b88dd4544a4196de1c53dfff40c70edb09f80374140b21c524f1ca8a354e7554468d0432c0fa006bfef22efd0ad0d096161661e998d218c7f6f3d51077e3fce114b88d6cd7251a6f4389589ef26f910bb83fd641316438582ca7bb19d8210ca3e8f2ed540d2f44b9f42b0e3614adbf7d81f0b6d65b58be7c3de1375564c7245faac5b2fda6f53ceb7dfcaa9142f9782825a595',
'c82ae3735cc0413709a571f0ed145592a694e9ccacad55e8a2a27a35715423eb1e5db587d1cf1898379879e271727db91c325b1e03747c3a795c30234acd1603f659469a7896d9083a8e84898f8b2e1e76ee790bc2bc1a8caa5f35a6893d29fde43bc6c12de5a50abdb0f3b9f2ce1db877ba3588cd9821a319f9cefc92f653ad7208f10eb3bb155f127c8cbae8f4f8f4b9f1d5cd7a7be3144ed2f08a97da102327b735ebfb37b471758b21b71d658a0f115cb52fe2c19318028965824f291223d93488ee798d8d7c2919f24ec956c2f8e0eedbbfa466f2264f4cea1fdf19cf99827737819234aaf3f0acebb647877adc9380aa431794f6daa476e89dffd4061ffb5352ad027ecf8bacbef8cb3fd07f89688b4c163a4b3778f49ac0a95a0aebab7d991b8c426f7feb35a817eba1a603a823a501037bf76b35fdf99d80e37a8ba75ecb8514215bd59d2662012d757c037a67d62a8200feb54a5584dc45970cb520480d1ec9fa80d6f269f4db152a5752dba94089fe108ea2d5ca8903e37db4610d979947830f9b32ce4a5b7fed68a9f8089965d72b469af06b0169a44af58494157a7a345cbc81d42ddd179bab443cf1cebef04f640be12cbd8dc85ab3d6dc7f9ba3d00bf417fe7a767d71c0f206881427bfadd51ec81ed1b903d81874175ab88dbe',
'c82ae3735cc0413709a571f0ed145592b48b5d556cac226989c4d4dbd2dc90a891908470772c03a2ffec81aacbf356532d6f4f159aea52d48d50e21af7caef05cc61cd540457ea5bbab78f2537ccefb8a157bb2dbb1cfe7c3808a98e05f26ab810858462b2d10ef64936a58ef39b956996664cf3067b27243310091571008e2ef0f74082fd16f089c0ccc55dc9f6fb96a40c8201e783a1a16b88a16ff67de5a10ee8561f33faf69faff402562fa413ba64bd787119995e95701c748f78fd13225f724b4ab6d6c2f371694e1a74f6dd3d0aa2aba6b328fd8827b4bc2c94dee5770710ec50f622a08089e6438810a77c5e6a7795f525a0a76705e03d867cae1e96df526c3af100f147aeea9fe6d9f80b0861b126a11fb42d226207e2d85e17332f7677d95ca288193226d0b34ef01e252386131a341024f080d3ee7cdde83d1c06539259b1850469d4ad3346d615be5e440a398f061b8eb41bc345a99003074896552fed306990922d082d35dc7e9ca734bb095c100ec8eb12a4efefb64c8e8ce6faa93caa13248c25eb9b5b8ed1617d86ac2a37adbed8743f8428',
'c82ae3735cc0413709a57130e9145592b802b2ca2b45182d9cb9186d93976b0ff391d00dd8d33e55c3183998b937743bcc94f80d7972f30e6e6293b33f4814c38a5b95a444a3bd62093adf6dc135edebf11e5c55b073bd6ef5a6ab5a924fd3624e5cbdd1147d9c0f2aedd7925e92d050f07081cee4f486bda5122df2d4fc1994de1be42a6a74fc1ecab541784a034f965332c768d82d80f0ea29f1e743bca59857bb57a9c419b4ac0f1266bd9a583e164cd6d10f9818c5ea0952416ca44ec47b1c88658e233cce2a339c1eb66fb610dddcd33120aecd2d252d17886d168ddcabd251d2a8e8beb07e99a35382ef41920ecd4a90933d83103ddd34d4629089d08cb3c7759eedeb7261961034b16db7b5ab78105ff1e2dccc229eee49a5c291ac05a2dce9f806f0a65707d606ef106a15b9b76f95e6b185e766a85d3cfea51a66d37ed58d44fb5decd0ba78789f5a9179c3f9de424c1180338931f9a8fe566aa9012603c8f3ab474ecbd40af9617160c7fb9f9b8bea6f13ae0ec4ee8421e92f64977e207de1c0650ab2d506c3322a883d8f259a6b3860831188f50a8d58cb68cc4c6a522b16801cc03c38fcf9d0fc8c0afedcb652f1b2f7e72cc93930f882b5da5c55ef44170b2cbd1489f79b475f91e2d820c0e0af06256ce4bc4b930279de31b82c8e63',
]

key=b'digitalpersona98'
    
for frag in frags:
    ct=unhexlify(frag)
    t=b''.join(validitea(key, ct, False))
    print(hexlify(t))