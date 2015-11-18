from common_classes import Animal, Genotype, Treatment, SubstanceAdministration, session
import datetime

ePet_wt = Genotype(name="ePet-cre", zygosity="wt")
ePet_tg = Genotype(name="ePet-cre", zygosity="Tg")
DAT_wt = Genotype(name="DAT-cre", zygosity="wt")

m1 = Animal(id_eth="4006", id_uzh="M3722", cage_eth="0003", cage_uzh="566113", sex="f", ear_punches="2R")
m1.genotype = [ePet_wt, DAT_wt]
session.add(m1)

m1 = Animal(id_eth="4007", id_uzh="M3716", cage_eth="0002", cage_uzh="570974", sex="m", ear_punches="L")
m1.genotype = [ePet_tg, DAT_wt]
SSRI = Treatment(substance="Fluoxetine", frequency="daily", route="IP")
SSRI.substance_administrations = [\
								SubstanceAdministration(date=datetime.datetime(2015,11,11,11,30,00)),
								SubstanceAdministration(date=datetime.datetime(2015,11,12,14,00,00), animal_weight=30.9, animal_weight_unit="g"),
								SubstanceAdministration(date=datetime.datetime(2015,11,13,15,45,00), animal_weight=30.8, animal_weight_unit="g"),
								SubstanceAdministration(date=datetime.datetime(2015,11,14,11,30,00)),
								SubstanceAdministration(date=datetime.datetime(2015,11,15,11,30,00), animal_weight=30.4, animal_weight_unit="g"),
								SubstanceAdministration(date=datetime.datetime(2015,11,16,11,30,00)),
								SubstanceAdministration(date=datetime.datetime(2015,11,17,11,30,00), animal_weight=29.5, animal_weight_unit="g")
								]
m1.treatment = [SSRI]
session.add(m1)

m1 = Animal(id_eth="4011", id_uzh="M2760", cage_eth="0004", cage_uzh="570971", sex="m", ear_punches="2L")
m1.genotype = [ePet_tg, DAT_wt]
m1.treatment = [SSRI]
session.add(m1)

m1 = Animal(id_eth="4012", id_uzh="M2758", cage_eth="0004", cage_uzh="570971", sex="m", ear_punches="R")
m1.genotype = [ePet_tg, DAT_wt]
m1.treatment = [SSRI]
session.add(m1)

m1 = Animal(id_eth="4013", id_uzh="M2757", cage_eth="0004", cage_uzh="570971", sex="m", ear_punches="L")
m1.genotype = [ePet_wt, DAT_wt]
session.add(m1)

m1 = Animal(id_eth="4001", id_uzh="M2763", cage_eth="0001", cage_uzh="570973", sex="f", ear_punches="LR")
m1.genotype = [ePet_tg, DAT_wt]
session.add(m1)

m1 = Animal(id_eth="4002", id_uzh="M2761", cage_eth="0001", cage_uzh="570973", sex="f", ear_punches="L")
m1.genotype = [ePet_tg, DAT_wt]
m1.treatment = [SSRI]
session.add(m1)

m1 = Animal(id_eth="4003", id_uzh="M2762", cage_eth="0001", cage_uzh="570973", sex="f", ear_punches="R")
m1.genotype = [ePet_wt, DAT_wt]
session.add(m1)

m1 = Animal(id_eth="4008", id_uzh="M4375", cage_eth="0006", cage_uzh="570972", sex="m", ear_punches="LR")
m1.genotype = [ePet_tg, DAT_wt]
session.add(m1)

m1 = Animal(id_eth="4009", id_uzh="M4374", cage_eth="0006", cage_uzh="570972", sex="m", ear_punches="R")
m1.genotype = [ePet_tg, DAT_wt]
m1.treatment = [SSRI]
session.add(m1)

m1 = Animal(id_eth="4010", id_uzh="M4373", cage_eth="0006", cage_uzh="570972", sex="m", ear_punches="L")
m1.genotype = [ePet_wt, DAT_wt]
session.add(m1)

m1 = Animal(id_eth="4004", id_uzh="M3718", cage_eth="0005", cage_uzh="570970", sex="f", ear_punches="L")
m1.genotype = [ePet_tg, DAT_wt]
m1.treatment = [SSRI]
session.add(m1)

m1 = Animal(id_eth="4005", id_uzh="M3721", cage_eth="0007", cage_uzh="570970", sex="f", ear_punches="2L")
m1.genotype = [ePet_tg, DAT_wt]
session.add(m1)

t1 = Animal(id_eth="4005", id_uzh="M3721", cage_eth="0007", cage_uzh="570970", sex="f", ear_punches="2L")
m1.genotype = [ePet_tg, DAT_wt]
session.add(t1)

session.commit()
