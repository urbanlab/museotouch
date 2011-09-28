from time import sleep, time
import pynfc

def print_targets(targets):
    for target in targets:
        nai = target.nti.nai
        print 'atqa:', map(hex, nai.atqa)
        print 'sak:', nai.sak
        print 'uid:', ' '.join(map(hex, nai.uid[:nai.uidlen]))

dev = pynfc.list_devices()[0]
nfc = dev.connect(target=False)

# Manual polling.
nmt_targets = (nfc.NMT_ISO14443A, nfc.NMT_ISO14443B)

while True:
    print '==== select passive'
    targets = []
    for nmt in nmt_targets:
        targets.extend(
            nfc.list_passive_targets(nmt, nfc.NBR_UNDEFINED))
    print_targets(targets)

'''
# NFC library polling
mod_targets = (
    pynfc.Modulation(nmt=nfc.NMT_ISO14443A, nbr=nfc.NBR_106),
    pynfc.Modulation(nmt=nfc.NMT_ISO14443B, nbr=nfc.NBR_106),
)

nfc.configure(nfc.NDO_INFINITE_SELECT, False)
iteration = 0
last_time = time()
while True:
    print '==== poll targets', iteration, '-', time() - last_time
    last_time = time()
    iteration += 1
    targets = nfc.poll_targets(mod_targets, 1, 2)
    print_targets(targets)
    #sleep(1)
'''
