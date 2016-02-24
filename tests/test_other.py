def perform_handover(x, y, *args, **kwargs):

    z = kwargs.get('z') #args[0]
    zz = kwargs.get('zz') # args[1]
    print('Foo ... %s, %s' % (z, zz))


if __name__ == "__main__":

    z = 22
    perform_handover(1, 2, z=z, zz=4)