# Python data structures preresenting the structure of
# JMRI conditionals


doverLogix = [
# IX:AUTO:0007C1  Dover 1
{
    'guard' : [
        ('Sensor', 'Dover - Track 1', 'INACTIVE') 
        ],
    'formula' : '',
    'action': [
        ('Sensor', 'Dover - Track 2', 'ACTIVE'),
        ('Sensor', 'Dover - Track 3', 'ACTIVE'),
        ('Sensor', 'Dover - Track 4', 'ACTIVE'),
        ('Sensor', 'Dover - Track 5', 'ACTIVE'),
        ('Sensor', 'Dover - DOB Reverse', 'ACTIVE'),
        ('Turnout', 'DOCW', 'NORMAL'),
        ('Turnout', 'DODW', 'NORMAL'),
        ('Turnout', 'DOFW', 'NORMAL'),
        ('Turnout', 'DOBe-xbW', 'NORMAL'),
        ('Sensor', 'IS5010', 'INACTIVE')
        ]
},
# IX:AUTO:0007C3  Dover 2
{
    'guard' : [ 
        ('Sensor', 'IS5002', 'INACTIVE')
    ],
    'formula' : '',
    'action' : [
        ('Turnout', 'DOBe-xbW', 'NORMAL'),
        ('Turnout', 'DOCW', 'REVERSED'),
        ('Turnout', 'DODW', 'NORMAL'),
        ('Turnout', 'DOFW', 'NORMAL'),
        ('Sensor', 'IS5001', 'ACTIVE'),
        ('Sensor', 'IS5003', 'ACTIVE'),
        ('Sensor', 'IS5004', 'ACTIVE'),
        ('Sensor', 'IS5005', 'ACTIVE'),
        ('Sensor', 'IS5007', 'ACTIVE'),
        ('Sensor', 'IS5010', 'INACTIVE')
    ]
},
# IX:AUTO:0007C23  DOB Normal Track 3 
{
    'guard' : [
        ('Sensor', 'IS5010', 'INACTIVE'),
        ('Turnout', 'DOFW', 'NORMAL'),
        ('Turnout', 'DODW', 'REVERSED')
    ],
    'formula' : '%s and %s and %s',
    'action' : [
        ('Sensor', 'IS5003', 'INACTIVE')
    ]
 },
 # IX:AUTO:0007C24  DOB Normal Track 4
{
    'guard' : [
        ('Sensor', 'IS5010', 'INACTIVE'),
        ('Turnout', 'DOFW', 'REVERSED'),
        ('Turnout', 'DOEW', 'NORMAL')
    ],
    'formula' : '%s and %s and %s',
    'action' : [
        ('Sensor', 'IS5004', 'INACTIVE')
        ]
},
# IX:AUTO:0007C17  DOK Normal
{
    'guard' : [ ('Sensor', 'IS5015', 'INACTIVE')],
    'formula' : '',
    'action' : [
        ('Turnout', 'DOK-xW', 'NORMAL'),
        ('Sensor', 'IS5011', 'ACTIVE')
    ]
},
# IX:AUTO:0007C37  Dover NX 3-11
{
    'guard' : [ 
        ('EntryExit', 'Dover NX 3 (G-DO-4RA) to Dover NX 11 (G-DO-10R)', 'ACTIVE') 
    ],
    'formula' : '',
    'action' : [ 
        ('Sensor', 'IS5006', 'INACTIVE'),
        ('Sensor', 'IS5007', 'INACTIVE')
    ]
}
]

class DoverListener(java.beans.PropertyChangeListener):
    def propertyChange(self, event):
        handleEvent(event, doverLogix)

def dover_virtual():
    dl = DoverListener()
    attachListener(doverLogix, dl)

dover_virtual()