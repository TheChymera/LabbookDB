from common_classes import Animal, Genotype, session

ePet_wt = Genotype(name="ePet-cre", zygosity="wt")
ePet_tg = Genotype(name="ePet-cre", zygosity="Tg")
DAT_wt = Genotype(name="DAT-cre", zygosity="wt")

m1 = Animal(id_eth="4006", id_uzh="M3722", cage_eth="0003", cage_uzh="566113", sex="f", ear_punches="2R")
m1.genotype = [ePet_wt, DAT_wt]
session.add(m1)

m1 = Animal(id_eth="4007", id_uzh="M3716", cage_eth="0002", cage_uzh="570974", sex="m", ear_punches="L")
m1.genotype = [ePet_tg, DAT_wt]
session.add(m1)

m1 = Animal(id_eth="4011", id_uzh="M2760", cage_eth="0004", cage_uzh="570971", sex="m", ear_punches="2L")
m1.genotype = [ePet_tg, DAT_wt]
session.add(m1)

m1 = Animal(id_eth="4012", id_uzh="M2758", cage_eth="0004", cage_uzh="570971", sex="m", ear_punches="R")
m1.genotype = [ePet_tg, DAT_wt]
session.add(m1)

m1 = Animal(id_eth="4013", id_uzh="M2757", cage_eth="0004", cage_uzh="570971", sex="m", ear_punches="L")
m1.genotype = [ePet_wt, DAT_wt]
session.add(m1)

m1 = Animal(id_eth="4001", id_uzh="M2763", cage_eth="0001", cage_uzh="570973", sex="f", ear_punches="LR")
m1.genotype = [ePet_tg, DAT_wt]
session.add(m1)

m1 = Animal(id_eth="4002", id_uzh="M2761", cage_eth="0001", cage_uzh="570973", sex="f", ear_punches="L")
m1.genotype = [ePet_tg, DAT_wt]
session.add(m1)

m1 = Animal(id_eth="4002", id_uzh="M2762", cage_eth="0001", cage_uzh="570973", sex="f", ear_punches="R")
m1.genotype = [ePet_wt, DAT_wt]
session.add(m1)

m1 = Animal(id_eth="4008", id_uzh="M4375", cage_eth="0006", cage_uzh="570972", sex="m", ear_punches="LR")
m1.genotype = [ePet_tg, DAT_wt]
session.add(m1)

m1 = Animal(id_eth="4009", id_uzh="M4374", cage_eth="0006", cage_uzh="570972", sex="m", ear_punches="R")
m1.genotype = [ePet_tg, DAT_wt]
session.add(m1)

m1 = Animal(id_eth="4010", id_uzh="M4373", cage_eth="0006", cage_uzh="570972", sex="m", ear_punches="L")
m1.genotype = [ePet_wt, DAT_wt]
session.add(m1)

m1 = Animal(id_eth="4004", id_uzh="M3718", cage_eth="0005", cage_uzh="570970", sex="f", ear_punches="L")
m1.genotype = [ePet_tg, DAT_wt]
session.add(m1)

m1 = Animal(id_eth="4005", id_uzh="M3721", cage_eth="0007", cage_uzh="570970", sex="f", ear_punches="2L")
m1.genotype = [ePet_tg, DAT_wt]
session.add(m1)

session.commit()
