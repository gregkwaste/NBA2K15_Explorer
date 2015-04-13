type_dict = {0x44445320: 'DDS',
             0xF07F68CA: 'MODEL',
             0x7EA1CFBB: 'OGG',
             0x305098F0: 'CDF',
             0x94EF3BFF: 'IFF',
             0x504B0304: 'ZIP',
             0x5A4C4942: 'ZLIB'}

archiveName_list = ['0A', '0B', '0C', '0D', '0E', '0F', '0G', '0H', '0I', '0J', '0K', '0L', '0M', '0N', '0O', '0P', '0Q', '0R', '0S', '0T', '0U', '0V', '0W', '0X', '0Y', '0Z',
                    '1A', '1B', '1C', '1D', '1E', '1F', '1G', '1H', '1I', '1J', '1K', '1L', '1M', '1N', '1O', '1P']

archiveName_discr = [' - Various 1', ' - Various 2', ' - Retro, Euro Teams', ' - Sixers', ' - Bucks', ' - Bulls', ' - Cavaliers', ' - Celtics', ' - Clippers', ' - Grizzlies', ' - Hawk', ' - Heat',
                     ' - Hornets', ' - Jazz', ' - Kings', ' - Knicks', ' - Lakers', ' - Magic', ' - Mavericks', ' - Nets', ' - Nuggets', ' - Pacers', ' - Pelicans', ' - Pistons', ' - Raptors', ' - Rockets', ' - Spurs',
                     ' - Suns', ' - Thunder', ' - Timberwolves', ' - Trailblazers', ' - Warriors', ' - Wizards', ' - Shaq and Ernie', ' - Shoes', ' - Create A Player', ' - Various Audio', ' - English Commentary', ' - Spanish Commentary', ' - MyTeam, Thumbs', ' - Updates 1', ' - Updates 2']

#for i in range(len(archiveName_list)): archiveName_list[i]+=archiveName_discr[i]

archiveOffsets_list = []
archiveName_dict = {}
settings_dict = {}
bool_dict = {'False': False,
             'True': True}
for i in range(len(archiveName_list)):
    archiveName_dict[archiveName_list[i]] = i
for i in range(len(archiveName_list)):
    settings_dict[archiveName_list[i]] = "False"

index_table = [0x63000000, 0x6E000000, 0x73000000, 0x74000000, 0x70000000]

zip_types = {0xE: 'LZMA', 0: 'NONE'}
version='0.29'
