import numpy as np
from struct import unpack
from math import ceil,floor

def sioread(**kwargs):
    '''
    Translation of Jit Sarkar's sioread.m to Python (which was a modification of Aaron Thode's with contributions from Geoff Edelman, James Murray, and Dave Ensberg).
    Hunter Akins
    June 4, 2019

     Input keys:
    	fname	(str)               Name/path to .sio data file to read
    	s_start		(int)    		Sample # to begin reading from (default 1). Must be an integer multiple of the record number. To get the record number you can run the script with s_start = 1 and then check the header for the info
    	Ns			(int)		    Total # of samples to read (default all)
    	channels	list of ints	Which channels to read (default all) (INDEXES AT 0)
    								Channel -1 returns header only, X is empty
    	inMem		bool            Perform data parsing in ram (default true)
    								False - Disk intensive, memory efficient
    									Blocks read sequentially, keeping only
    									requested channels. Not yet implemented
    								True  - Disk efficient, memory intensive
    									All blocks read at once, requested
    									channels are selected afterwards

     Output parameters:
    	X			array(Ns,Nc)	Data output matrix
    	Header	    dictionary		Descriptors found in file header

    '''

    if 'fname' not in kwargs.keys():
        raise ValueError("must pass me a filename")
    file_name = kwargs['fname']

    with open(file_name, 'rb') as f:
        # Parameter checking
        s_start = 1
        if 's_start' in kwargs.keys():
            tmp = kwargs['s_start']
            s_start = max(tmp, 0)

        if 'Ns' in kwargs.keys():
            Ns = kwargs['Ns']
        else:
            Ns = -1

        if 'channels' in kwargs.keys():
            channels = kwargs['channels']
        else:
            channels = []


        if 'inMem' in kwargs.keys():
            inMem = kwargs['inMem'] # false will read whole file before subsetting
        else:
            inMem = True

        # Endian check
        endian	=	'>'
        f.seek(28)
        bs	= unpack(endian +  'I', f.read(4))[0]		# should be 32677
        if bs != 32677:
            endian	=	'<'
            f.seek(28)
            bs	=unpack(endian + 'I', f.read(4))[0]	# should be 32677
            if bs != 32677:
                raise ValueError('Problem with byte swap constant:' + str(bs))

        f.seek(0)
        ID	= int(unpack(endian + 'I', f.read(4))[0])	# ID Number
        Nr	= int(unpack(endian + 'I', f.read(4))[0])	# # of Records in File
        BpR	= int(unpack(endian + 'I', f.read(4))[0])	# # of Bytes per Record
        Nc	= int(unpack(endian + 'I', f.read(4))[0])	# # of channels in File
        BpS	= int(unpack(endian + 'I', f.read(4))[0])	# # of Bytes per Sample
        if BpS == 2:
            dtype = 'h'
        else:
            dtype = 'f'
        tfReal = unpack(endian + 'I', f.read(4))[0] # 0 = integer, 1 = real
        SpC  = unpack(endian + 'I', f.read(4))[0] # # of Samples per Channel
        bs  = unpack(endian + 'I', f.read(4))[0] # should be 32677
        fname = unpack('24s', f.read(24)) # File name
        comment = unpack('72s', f.read(72)) # Comment String

        RpC  = ceil(Nr/Nc)   # # of Records per Channel
        SpR  = int(BpR/BpS)          # # of Samples per Record

        # Header object, for output
        Header = {}
        Header['ID'] = ID
        Header['Nr']  = Nr
        Header['BpR']  = BpR
        Header['Nc']  = Nc
        Header['BpS'] = BpS
        Header['tfReal'] = tfReal
        Header['SpC']  = SpC
        Header['RpC']  = RpC
        Header['SpR']  = SpR
        Header['fname'] = fname
        Header['comment'] = comment
        Header['bs']  = bs
        Header['Description'] = """
                    ID= ID Number
                    Nr  = # of Records in File
                    BpR = # of Bytes per Record
                    Nc  = # of channels in File
                    BpS = # of Bytes per Sample
                    tfReal = 0 - integer, 1 - real
                    SpC = # of Samples per Channel
                    fname = File name
                    comment= Comment String
                    bs  = Endian check value, should be 32677
                    """


        # if either channel or # of samples is 0, then return just header
        if  (Ns == 0):
            X	=	[]
            return X, Header

        if (len(channels) == 1) and (channels[0] == -1):
            X	=	[]
            return X, Header


        # Recheck parameters against header info
        Ns_max = SpC - s_start + 1;
        if	Ns == -1:
            Ns	=	Ns_max			#	fetch all samples from start point
        if Ns > Ns_max:
            print('More samples requested than present in data file. Return max num samples:', Ns_max)
            Ns	=	Ns_max

        # Check validity of Channeli list
        if len(channels) == 0:
            channels	=	list(range(Nc))	#	fetch all channels
        if (len([x for x in channels if (x < 0) or (x > (Nc - 1))]) != 0):
            raise ValueError('Channel #s must be within range 0 to ' + str(Nc - 1))


        ## Read in file according to specified method
        # Calculate file offsets
        # Header is size of 1 Record at beginning of file
        r_hoffset	=	1
        # Starting and total records needed from file
        r_start	=int( floor((s_start-1)/SpR)*Nc + r_hoffset)
        r_total	= int(ceil(Ns/SpR)*Nc)

        # Aggregate loading
        if	inMem:
            # Move to starting location
            f.seek( r_start*BpR)

            # Read in all records into single column
            if dtype == 'f':
                Data	=	unpack(endian + 'f'*r_total*SpR, f.read( r_total*SpR*4))
            else:
                Data	=	unpack(endian + 'h'*r_total*SpR, f.read( r_total*SpR*2))
            count = len(Data)
            Data = np.array(Data) # cast to numpy array
            if	count != r_total*SpR:
                raise ValueError('Not enough samples read from file')

            #	Reshape data into a matrix of records
            Data	=	np.reshape(Data, (r_total, SpR)).T

            #	Select each requested channel and stack associated records
            m	=	int(r_total/Nc *SpR)
            n	=	len(channels)
            X	=	np.zeros((m,n))
            for	i in range(len(channels)):
                chan	=	channels[i]
                blocks = np.arange(chan, r_total, Nc, dtype='int')
                tmp	=	Data[:, blocks]
                X[:,i]	=	tmp.T.reshape(m,1)[:,0]

            # Trim unneeded samples from start and end of matrix
            trim_start	=	int((s_start-1)%SpR)
            if	trim_start != 0:
                X = X[trim_start:,:]
            [m,tmp]	=	np.shape(X)
            if	m > Ns:
                X = X[:int(Ns), :]
            if	m < Ns:
                raise ValueError('Requested # of samples not returned. Check that s_start is multiple of rec_num: ' + str(SpR))


        # Incremental loading
        else:
            print('Not yet implemented incremental loading')

    return X, Header


class SioStream:
    """
    data object implementing indexing and return sequential data
    Indexing starts out 0, but sioread indexes at 1, so I need to add 1 to all keys
    """
    def __init__(self, fname):
        s_start, Ns = 1, 1
        inp = {'fname': fname, 's_start': s_start, 'Ns':Ns}
        [tmp, hdr] = sioread(**inp)
        # use header to get Nc and samples per channel
        self.Nc = hdr['Nc']
        self.SpC = hdr['SpC']
        self.SpR = hdr['SpR']
        self.inp = inp

    def __getitem__(self, key):
        if isinstance(key, slice):
            if key.step is None:
                step = 1
            else:
                step = key.step
            start = key.start
            resid = start % self.SpR
            if resid != 0:
                start -= resid
                self.inp['s_start'] = start+1
                if key.stop is None:
                    self.inp['Ns'] = 1
                else:
                    self.inp['Ns'] = key.stop - key.start + resid
                [tmp, hdr] = sioread(**self.inp)
                tmp = tmp[resid:] # truncate the unnecessary read at beg.
                return tmp
        self.inp['s_start'] = key.start+1
        if key.stop is None:
            self.inp['Ns'] = 1
        else:
            self.inp['Ns'] = key.stop - key.start
        [tmp, hdr] = sioread(**self.inp)
        return tmp
