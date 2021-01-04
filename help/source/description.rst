Struktura programu
==================

Struktura programu RadAgro byla definována na základě předpokladu
ztráty, respektive změny aktivity v prostředí, která je daná na jedné
straně odnosem radionuklidu z prostředí, na druhé straně vlastním
radioaktivním rozpadem radionuklidu. Hlavními faktory, které mohou
ovlivnit přítomnost radionuklidu v prostředí jsou:

* odnos ve vodním prostředí (odtok)
* odnos na částicích půdy vlivem eroze půdy
* odnos v biomase vlivem jejího odstranění (sklizeň)
* radioaktivní přeměna

Přehled základní struktury modelu ukazuje obrázek.

.. image:: figs/models/zakl_schema.png
    :align: center

Je potřeba poznamenat, že uvedené faktory jsou provázané a působí
synergicky. Vazby mezi jednotlivými vstupy a procesy ukazuje
následující schéma:

.. image:: figs/models/schema_vazby.png
    :align: center
    :scale: 70%

Vlastní výpočet časových změn radioaktivní kontaminace území je
rozdělen do dvou částí, na výpočet situace v časné fázi radiační
události a na výpočet změn kontaminace v následujícím období v
měsíčním kroku.

V časné fázi radiační události je pozornost zaměřena na otázku
rozdělení radioaktivní depozice mezi porost a půdu a případnou
možnost omezení kontaminace půdy odstraněním kontaminované nadzemní
biomasy. Časná fáze představuje časové období v trvání několika dnů
až týdnů.

Následující střednědobá až dlouhodobá fáze navazuje na časnou fázi
radiační události. V programu RadAgro je tato fáze pojata jako
sekvence střídajících se období, která zahrnuje vliv střídání plodin
na pozemcích, jejich management, erozi a současně i radioaktivní
přeměnu kontaminujícího radionuklidu.

V následujícím textu jsou popsány jednotlivé složky výpočtu
radioaktivní kontaminace v časné a následné (střednědobé a dlouhodobé)
fázi radiační události.


Časná fáze
----------

V časné fázi radiační události, tj. od začátku úniku radionuklidu do
prostředí po dobu několika hodin až dnů, případně až týdnů je zásadní
získání  informací o depozici radionuklidu na porostech plodin a na
povrchu půdy a o vlastnostech plodin. Tyto informace jsou zásadní pro
provedení opatření pro ochranu půdy a tedy i životního prostředí
(vody, organismů atd.). Jestliže známe množství kontaminované
biomasy, úroveň její kontaminace a prostorovou distribuci, můžeme
efektivně plánovat a provádět odstranění biomasy plodin z pozemků.

Program RadAgro umožňuje odhadnout velikost efektu odstranění biomasy
v časné fázi na snížení radioaktivní kontaminace prostředí (půdy).
Odhad je založen na růstové analýze plodin a výpočtu
intercepčního faktoru pro daný radionuklid. Zároveň je celé území
rozděleno do tří skupin podle referenčních úrovní kontaminace, v
závislosti na možnostech dalšího managementu území (viz dále).


Střednědobá a dlouhodobá fáze
------------------------------

Střednědobá a dlouhodobá fáze radiační události představuje období v
délce trvání měsíců až let. Program RadAgro umožňuje odhad vývoje v
měsíčním kroku na období až 166 let. Limitace je zde dána omezením
výstupního formátu vektorové vrstvy vývoje radioaktivní kontaminace
území.

Rozdíl oproti časné fázi spočívá ve změně sledování jednotlivých
faktorů změny radioaktivní kontaminace území. Zatímco v časné fázi je
předpokladem, že biomasa plodin je překážkou pro radionuklid na které
se část kontaminace zachytí, v dlouhodobé fázi rozhoduje více faktorů.

Prvním z faktorů je management. Program RadAgro v zásade řeší jako
hlavní managementové opatření střídání plodin v osevním postupu.
Jednotlivé plodiny mají zásadní význam pro snižování radioaktivní
kontaminace půdy vlivem absorpce kontaminantu, která je dána
transferovým koeficientem. Snížení kontaminace plochy je pak dáno
odstraněním nadzemní biomasy plodin při sklizni.
Plodiny a jejich střídání v osevním postupu mají významný vliv na
erozi půdy, která je dalším zásadním faktorem při snižování
kontaminace půdy/plochy a na odtokové vlastnosti povrchu, tedy na
hydrologii území.

Vedle managementu, eroze a hydrologie má na snižování
radioaktivní kontaminace samozřejmě významný vliv též radioaktivní
přeměna radionuklidu.

V následujícím textu jsou popsány jednotlivé sledované parametry a
způsob jejich výpočtu.


Růstová analýza
================

Růstová analýza je v programu RadAgro využita pro odhad parametrů
plodin, které jsou zásadní pro následný odhad radioaktivní
kontaminace nadzemní biomasy plodin a půdy. Jedná se o odhad množství
sušiny nadzemní biomasy plodin a o odhad pokryvnosti listoví, které
jsou využity v časné fázi radiační události, odhad množství sušiny je
pak využit též v dlouhodobém pohledu.

Sušina nadzemní biomasy
------------------------

Model výpočtu šušiny nadzemní biomasy je založen na předpokladu,
že přírůst sušiny plodin odpovídá sigmoidní (logistické) křivce v
závislosti na čase. Množství sušiny nadzemní biomasy :math:`W \ (t
.ha^{-1})` lze vypočítat následovně:

.. math::
    :label: dry_w

    W=\frac{W_{max}}{1+\mathrm{e}^{-t}}

kde :math:`W_max` je maximální množství sušiny v produkci plodiny
:math:`(t.ha-1)` a :math:`t` je škálovanou funkcí času, za
předpokladu, že se křivka při zvolené hodnotě asymptoticky blíží
limitním hodnotám. Hodnotu :math:`t` vypočteme podle vzorce:

.. math::
    :label: t_value

    t=m\cdot t_{s}-n

kde :math:`m` a :math:`n` jsou parametry specifické pro jednotlivé
plodiny a :math:`t_{s}` je škálovaná hodnota času vypočtená podle
vzorce:

.. math::
    :label: ts

    t_{s}=\frac{t_{akt}-t_{0}}{t_{max}-t_{0}}

kde :math:`t_{akt}` je hodnota pro daný den v rámci uvažovaného období,
:math:`t_{0}` je minimální uvažovaná hodnota (např. den výsevu) a
:math:`t_{max}` je maximální hodnota (např. den sklizně), kdy
množství sušiny dosahuje maxima.

Vlastní parametry plodin :math:`n` a :math:`m` lze zjistit na základě
kalibrace růstového modelu skutečným průběhem růstu dané plodiny
během vegetačního období pomocí úpravy rovnice :eq:`dry_w` a s využitím
lineární regrese následujícím způsobem:

.. math:: \mathrm{e}^{-t}=\frac{W_{max}}{W}-1
    :label: w_ratio

Logaritmováním rovnice získáme výraz:

.. math::
    :label: minus_t

    -t=\ln\left(\frac{W_{max}}{W}-1\right)

a kombinací rovnic :eq:`w_ratio` a :eq:`minus_t` získáváme výledný tvar
rovnice:

.. math::
    :label: minus_ln

    -\ln\left(\frac{W_{max}}{W}-1\right)=m\cdot t_{s}-n

kdy na základě známých hodnot :math:`W_{max}` a :math:`W` lze s
využitím lineární regrese vypočítat hodnoty :math:`m` a :math:`n`.
Pro účely programu RadAgro jsou pro jednotlié plodiny parametry
:math:`m` a :math:`n` stanoveny na základě změny sklonu regresní
křivky mezi předpokládanou minimální a maximální hodnotou množství
sušiny a hodnot :math:`t_{s}` pro počáteční a konečný termín
sledovaného období. Hodnoty parametrů :math:`m` a :math:`n` jsou
v rámci zadání hodnot do uživatelského rozhraní programu načteny do
tabulky v záložce Parametry, list Rstový model, kde je možné je ručně
změnit. S ohledem na matematické vyjádření rovnice :eq:`minus_ln`, kdy
nelze vypočítat přirozený logaritmus nulové a záporné hodnoty, byla
tato rovnice upravena následovně:

.. math::
    :label: minus_t_corr

    -t=\ln\left(\left|\frac{W_{max}}{W-0.001}-1\right|\right)

kde :math:`W` je minimální hodnota množství sušiny v případě počátečního
termínu a maximální hodnota v případě konečného uvažovaného termínu
:math:`(W=W_{max})`.

Výpočet množství sušiny plodin předpokládá jednoletost plodin a
období jejich vegetace od doby setí do doby sklizně v případě
jařin a nebo od jarních měsíců, kdy jsou tradičně vysévány jařiny do
sklizně v případě ozimů. Podzimní období u ozimů není bráno v potaz s
ohledem na malé množství biomasy.

Pokryvnost listoví
------------------

Dalším významným produkčním ukazatelem porostu je pokryvnost 
listoví nebo též index listové plochy (:math:`LAI`,
:math:`m^{2}\cdot m^{-2}`), který je využit
pro odhad radiační kontaminace biomasy a povrchu půdy. Vlastní
průběh vypočtené křivky :math:`LAI` je odvozen z průběhu růstu
biomasy a značně generalizován. Časová změna :math:`LAI` pro
určitou plodinu je vypočtena v krocích následovně:

.. math::
    :label: LAI

    LAI=\begin{cases}
        LAI_{max}^{2}\cdot\frac{W}{W_{max}}; & \quad pro\quad t_{s}<0.7\\
        X; & \quad pro\quad t_{s}\geq0.7\\
        LAI_{max}; & \quad pro\quad LAI\geq LAI_{max}
    \end{cases}

kde :math:`LAI_{max}` je maximální pokryvnost listové plochy pro danou
plodinu. :math:`X` je empirická funkce:

.. math::
    :label: x_eq

    X=\left(3.6511\cdot LAI+0.19993\cdot RWC_{min}-6.66309\right)\cdot t_{s}^{2}+\left(3.9841\cdot LAI_{max}-0.14\cdot RWC_{min}+4.6668\right)\cdot t_{s}

Obdobně, jako v případě výpočtu množství sušiny plodin předpokládá
výpočet :math:`LAI` jednoletost plodin a období jejich vegetace od
doby setí do doby sklizně v případě jařin a nebo od jarních měsíců,
kdy jsou tradičně vysévány jařiny do sklizně v případě ozimů.
Podzimní období u ozimů není bráno v potaz s ohledem na malé množství
biomasy.


Kontaminace zeleně a půdy, intercepční faktor
----------------------------------------------

Pro rozhodování o množství depozice radioaktivního materiálu na povrchu
porostu a povrchu půdy je vypočten intercepční faktor (rel.), který je
ukazatelem, jak velká frakce depozice zůstává na povrchu porostu. Hodnota
závisí na indexu listové plochy porostu a úhrnu srážek v průběhu depozice.
Podle Müllera a Pröhla (1993) lze intercepční frakci (faktor) depozice
radioizotopu fw v časné fázi radiační havárie vypočítat podle vzorce:

.. math::
    :label: int_f

    f_{w}=\min\left[0.8;\frac{LAI\cdot k\cdot S\left(1-\mathrm{e^{-\frac{\ln2}{3S}R}}\right)}{R}\right]

kde k je specifický faktor pro daný kontaminant (I: k = 0.5; Sr, Ba:
k = 2; Cs a ostatní radionuklidy: k = 1), S je tloušťka vodního filmu
na rostlinách (mm) a R je úhrn srážek (mm). Hodnota S je zpravidla 0,
15 – 0,3 mm se střední hodnotou 0,2 mm (Pröhl, 2003). Výpočet
depozice na povrchu rostlin vychází z předpokladu, že depozice na
povrchu rostlin je poměrnou částí celkové depozice danou intercepčním
faktorem:

.. math::
    :label: depo_plants

    D_{biomasa}=D_{celk}\cdot f_{w}

kde :math:`D_{biomasa}` je měrná depozice radioizotopu na povrchu rostlin
:math:`(Bq.m^{-2})` a Dcelk je celková měrná radioaktivní depozice :math:`(Bq
.m^{-2})` zadávaná jako vstup do modelu. Měrná depozice radioizotopu na
povrchu půdy (Dpuda ; :math:`Bq.m^{-2}`) je pak rozdílem mezi celkovou měrnou
depozicí a měrnou depozicí na povrchu porostu:

.. math::
    :label: depo_soil

    D_{puda}=D_{celk}-D_{biomasa}

Pokud jsou hodnoty vypočteného množství biomasy menší než 0,5 :math:`t
.ha^{-1}`, je vypočtena pouze měrná depozice radioaktivního materiálu na
povrchu půdy. Důvodem je minimální předpoklad možnosti odstranění biomasy.


Hydrologie
==========

Hydrologický model nebyl do vlastního výpočtu změn radioaktivní
kontaminace implementován ze dvou důvodů. Prvním důvodem je
předopkládaný minimální efekt změny radioaktivní kontaminace vlivem
odnosu radionuklidu v odtékající vodě povrchovým nebo podpovrchovým
odtokem. Efektivitu odhadujeme na úrovni jednotek promile z celkové
změny měrné aktivity na sledovaných plochách. Druhým důvodem je
výpočetní náročnost a čas potřebný na výpočet. Náročnost výpočtu
vychází z potřeby cyklických změn formátu dat mezi rastrem a vektorem
a z potřeby komplikovaných maticových výpočtů srážkoodtokového modelu.
Všechny potřebné metody hydrologického modelu jsou obsaženy v modulu
waterflow a jsou dále popasány v následujícím textu.

Schéma výpočtu hydrologických charakteristik ukazuje schéma:

.. image:: figs/models/schema_hydro.png
    :align: center
    :scale: 70%

Výpočet akumulace odtoku z území
---------------------------------

Výpočet je založen na metodě výpočtu akumulace odtoku z území. Metoda
je založena na výpočtu pravděpodobnosti odtoku vody ze zdrojového
pixelu digitálního modelu území do akumulačního pixelu v závislosti na:

* sklonitosti
* délce dráhy odtoku mezi pixely
* odporu povrchu pro odtok vody z daného pixelu.

Výpočet probíhá iterativně, kdy bere v potaz výpočet
předchozí, čímž dochází k sumaci odtoku.

Výpočet se provádí od pixelu s nejvyšší nadmořskou výškou směrem
dolů, vždy pro matici 3x3. Výpočetní matici označíme podle světových
stran:

.. image:: figs/models/flacc_orient.png
    :align: center
    :scale: 30%

*Označení buněk rastru podle prostorové orientace. Označení odpovídá
světovým stranám: N – sever, NE – severovýchod, E – východ atd.*

Jestliže uvažujeme, že funkcí pravděpodobnosti odtoku vody z
centrálního pixelu do ostatních pixelů je výškový rozdíl mezi pixely
(viz např. Stum 2017) a vzdálenost jednotlivých pixelů, potom  můžeme
definovat geometrii odtoku vody podle schématu:

.. image:: figs/models/flacc_geom.png
    :align: center
    :scale: 40%

*Schématické vyjádření geometrie mezi dvěma pixely DMT s odlišnou
nadmořskou výškou. :math:`h` je rozdíl výšek, :math:`d` je vzdálenost
mezi středy dvou pixelů*

kde :math:`h` je rozdíl nadmořské výšky mezi jednotlivými pixely a
:math:`d` je vzdálenost mezi středy centrálního pixelu a jednotlivých
ostatních pixelů. Vertikální a horizontální vzdálenosti mezi
středy pixelů jsou shodné s velikostí pixelů ve vertikálním a
horizontálním směru. Označíme-li horizontální velikost pixelu symbolem
:math:`x` a vertikální symbolem :math:`y`, potom

.. math::
    :label: d_value

    d = x
    d = y

pro diagonální směr je vzdálenost středů pixelů

.. math::
    :label: d_diag

    d = \sqrt{x^2+y^2}

Známe-li rozdíly nadmořské výšky, velikost jednotlivých pixelů a
vzdálenost mezi jejich středy, potom pravděpodobnost odtoku vody
škálovanou v intervalu :math:`\langle 0, 1 \rangle` vypočteme podle
vztahu:

.. math::
    :label: p_i_value

    p_i=\frac{2\cdot \arctan \frac{h}{d}}{\pi}

Uvedený vztah platí pouze pro kladné hodnoty rozdílu nadmořské výšky
mezi centrálním a okrajovými pixely (voda teče s kopce). V opačném
případě platí, že

.. math::
    :label: p_i_zero

    p_i=0

Model akumulace pravděpodobnosti odtoku předpokládá hladký povrch pro
odtok, kdy je odtok dán pouze geometrií povrchu. Při povrchovém
odtoku vody z území lze nicméně předpokládat vliv vlastního povrchu
na odtok. Zde můžeme uvažovat o odporu povrchu pro odtok vlivem jeho
drsnosti, který můžeme vyjádřit např. jako Manningův koeficient
drsnosti nebo jako Darcyho-Weinsbachův koeficient drsnosti v
intervalu :math:`\langle 0, 1 \rangle` (označ. :math:`n`).
Výsledný vzorec pro pravděpodobnost odtoku bude mít tvar:

.. math::
    :label: p_i_manning

    p_i=p_i(1-n)

Protože pracujeme s maticí hodnot, je výsledná pravděpodobnost odtoku
vody z centrálního pixelu pro jednotlivé pixely rovna:

.. math::
    :label: p_j_matrix

    p_j=\frac{p_i}{\displaystyle\sum_{0}^{i=8} p_i}

přičemž

.. math::
    :label: p_j_sum

    \displaystyle\sum_{0}^{j=8} p_j = 1

tzn., že výsledný součet všech pravděpodobností odtoku vody z
centrálního pixelu v matici se rovná 1. V případě, že je v matici ve
všech případech nulový sklon, tedy jedná se o rovinu, je
pravděpodobnost odtoku do jednotlivých pixelů vypočtena jako 1/8
celkové pravděpodobnosti odtoku vody z centrálního pixelu.
Vlastním výsledkem výpočtu je matice pravděpodobnosti odtoku
:math:`fl_{prob}`.
Předpokládáme-li, že veškerá srážková voda odtéká povrchovým odtokem,
je akumulace odtoku :math:`(flowacc)` rovna součinu množství srážek
:math:`(P)` a pravděpodobnosti akumulace odtoku:

.. math::
    :label: flowacc

    flowacc=P\cdot fl_{prob}

Výpočet hydrologické bilance v území
-------------------------------------

Výpočet hydrologické bilance je do značné míry problematický a
zahrnuje celou řadu faktorů. Aby bylo možné predikovat srážkoodtokové
parametry území ve střednědobém a dlouhodobém časovém měřítku, byl
upraven epizodní hydrologický model CN křivek pro měsíční krok výpočtu.
Pro výpočet hydrologické bilance je potřeba určit následující ukazatele:

* průměrné měsíční úhrny srážky, případně měsíční úhrny srážek
* hlavní půdní jednotka (HPJ)
* plodinu a osevní postup
* hydrologický stav plochy
* index listové plochy

Pomocí uvedených ukazatelů vypočteme ukazatele potřebné pro výpočet složek hydrologické bilance:

* intercepci vody na povrchu
* CN křivku plochy (pixelu)
* maximální potenciální retenční schopnost půdy

A ve výsledku vypočteme složky hydrologické bilance:

* povrchový odtok
* retence vody v půdě
* výpar vody

Použitý přístup pracuje na úrovni jednotlivých pixelů, kdy je
předpokládána akumulace odtoku v rámci jednotlivých pixelů.

Faktory potřebné pro výpočet:

**Úhrn srážek**

Úhrny srážek jsou uvažovány jako měsíční úhrny, pro účely použití
modelu pro predikce je uvažováno, že jsou použity měsíční normály. V
případě, že je použito větší množství meteorologických stanic v
území, je úhrn srážek interpolován buď pomocí Thiessenových polygonů
nebo jiným způsobem. Úhrny srážek jsou uváděny v mm.

**Hlavní půdní jednotky**

Hlavní půdní jednotky (HPJ) jsou definovány vyhláškou 227/2018 Sb. Pro
účely programu RadAgro jsou použity kódy 1-78, které lze získat z map
BPEJ poskytovaných Výzkumným ústavem meliorací a ochrany půd.
HPJ slouží k rozdělení půd podle hydrologické charakteristiky do
hydrologických půdních skupin A, B, C a D, na základě kterých je
následně odhadnuto číslo CN křivek. Prů účely erozního modelu je HPJ
využita pro stanovení K faktoru rovnice USLE.

**Plodina**

Plodiny jsou prostorově definovány na základě terénního průzkumu
nebo pomocí DPZ a dále je definována časová řada obsahující
jednotlivé plodiny v osevním postupu. Vstupní vrstva (vektorová)
obsahuje prostorovou distribuci plodin a jednotlivých ostatních
ploch s vegetačním krytem (lesy, ostatní plochy).

**Hydrologický stav ploch**

Jedná se o tabelární hodnoty určující chování modelu. Hodnoty jsou v
programu určeny na základě hydrologického stavu půd (dobrý a špatný).

**Index listové plochy**

Index listové plochy je počítám na základě růstové analýzy (viz výše).

**CN křivky**

Hodnoty CN křivek určují schopnost retence půdy na dané ploše. Jejich
odvození vychází z vlastností půd, jejich hydrologického stavu,
vegetačního pokryvu a managementu. Hodnoty CN křivek jsou udávány
jako tabelární hodnoty.

Separace odtoku
++++++++++++++++

Hydrologický model je založen na separaci odtoku založené na metodě
CN křivek (podrobnosti viz např. Janeček a kol. 2012).

Výpočet povrchového odtoku :math:`R` je založen na vztahu:

.. math::
    :label: runoff

    R=\frac{(P-I)^2}{P-I+S_{max}}

kde :math:`P` je celkový úhrn srážek za dané období :math:`(mm)`,
:math:`I` jeintercepce :math:`(mm)` a :math:`S_{max}` je maximální
potenciální ztráta na povodí (maximální retence; :math:`mm`).

Model vychází z předpokladu, že velikost intercepce bude úměrná
listové ploše a velikosti úhrnu srážek. Intercepce v měsíčním kroku
se vypočte podle vztahu:

.. math::
    :label: intercept

    I=a\cdot P \mathrm{e}^{b\cdot LAI}

kde :math:`I` je intercepce :math:`(mm)`, :math:`P` je úhrn srážek
:math:`(mm)`, :math:`LAI` je index listové plochy
:math:`(m^2.m^{-2})`, :math:`a` a :math:`b` jsou empiricky
odvozené konstanty :math:`(a = 0.1; \ b = 0.2)`, které lze změnit v
uživatelském rozhraní programu.

Hodnota maximální retence :math:`S_{max}` byla vypočtena podle vztahu:

.. math::
    :label: max_ret

    S_{max}=25.4\frac{1000}{CN-10}

Jestliže je celkový úhrn srážek menší než :math:`0.2S_{max}`, je
výsledná hodnota :math:`R` rovna nulovému odtoku.
Vlastní aktuální retence vody :math:`S` je vypočtena podle vztahu:

.. math::
    :label: retence

    S=P-I-R

Srážko-odtokový model je založen na akumulaci odtoku (viz kapitola
Výpočet akumulace odtoku z území), z tohoto důvodu
je v rámci výpočtu akumulace odtoku uvažováno množství vody
vstupující do výpočtu, které je tvořeno součtem množství srážek
(:math:`P_i`) a množství povrchového odtoku z předchozího kroku
výpočtu (:math:`P_{i-1}`), tedy:

.. math::
    :label: P_celk

    P_{tot} = P_i - P_{i-1}

Evapotranspirace
+++++++++++++++++

Vzhledem k tomu, že je výpočet založen na časovém kroku jednoho
měsíce, je do výpočtu zahrnuta problematika evapotranspirace a
hodnoty :math:`S` a :math:`R` jsou korigovány. Jako vstupní parametr
je využit výpočet potenciální evapotranspirace (ETp) podle
Thornthwaita (1948):

.. math::
    :label: etp_thorn

    ET_p=16\frac{N}{30}\frac{s_0}{12}\left(\frac{10T_m}{I_c}\right)^a

kde :math:`N` je počet dnů v měsíci, :math:`s_0` průměrná délka trvání
slunečního
svitu (:math:`h`), :math:`T_m` je průměrná měsíční teplota vzduchu
(°C), :math:`I_c` je
teplotní index a :math:`a` je konstanta. Průměrná délka trvání
slunečního svitu pro daný měsíc :math:`s_0` byla vypočtena na základě
zeměpisné šířky.

Teplotní index :math:`I_c` byl vypočten jako součet dílčích měsíčních
teplotních indexů :math:`i_j`:

.. math::
    :label: temp_ind

    I_c=\displaystyle\sum_{j=1}^{12} i_j

kde

.. math::
    :label: index_i

    i_j=\left(\frac{T_j}{5} \right)^{1.514}

kde :math:`T_j` je průměrná měsíční teplota pro danou lokalitu pro
jednotlivé měsíce (°C). Exponent :math:`a` byl vypočten podle vztahu:

.. math::
    :label: expon_a

    a=({0.0675 I_c^{3}} - {7.71 I_c^{2}}+{1792 I_c}+7239)\cdot 10^{−5}

Aktuální evapotranspirace byla vypočtena na základě potenciální
evapotranspirace a úhrnu srážek (Ol'dekop (1911), citováno v
Brutsaert (1992) a Xiong & Guo (1999)) podle vztahu:

.. math::
    :label: act_et

    ET_a=ET_p\tanh \left(\frac{P}{ET_p} \right)

Korekce odtoku
+++++++++++++++

Vlastní korekce povrchového odtoku (:math:`R_{cor}`) a retence
(:math:`S_{cor}`) je založena na rozdělení úhrnu evapotranspirace na
výpar z půdy a výpar z povrchového odtoku:

.. math::
    :label: r_cor

    R_{cor} = R - c_R(ET_a-I)

a

.. math::
    :label: s_cor

    S_{cor} = S - c_S(ET_a-I)

kde :math:`c_R` a :math:`c_S` jsou koeficienty odvozené jako poměr
výparu z retence vody (z půdy) a z přímého odtoku:

.. math::
    :label: cr_const

    c_R=\frac{c_aR}{c_aR+c_bS}

a

.. math::
    :label: cs_const

    c_S=1-c_R

Konstanty :math:`c_a` a :math:`c_b` byly stanoveny následovně:

.. math::
    :label: ca_const

    c_a=a\cdot \mathrm{e}^{aP_{tot}}

a

.. math::
    :label: cb_const

    c_b=bCN + c

kde :math:`a`, :math:`b` a :math:`c` jsou konstanty, které lze upravit
v uživatelském rozhraní programu.

Erozní model
=============

Odnos půdy z pozemků je důležitým faktorem, který ovlivňuje změnu
zátěže půdy radioaktivní kontaminací. Odnos půdy byl definován na
základě univerzální rovnice ztráty půdy (USLE), vyjádřené rovnicí:

.. math::
    :label: usle

    G=R \cdot K \cdot L \cdot S \cdot C \cdot P

kde

* :math:`G` je průměrná dlouhodobá ztráta půdy
  (:math:`t.ha^{-1}.rok^{-1}`). Pro vlastní výpočet je hodnota
  uvažována pro měsíční chod)
* :math:`R` je faktor erozní účinnosti dešťů, vyjádřený v závislosti na
  kinetické energii, úhrnu a intenzitě erozně nebezpečných dešťů
* :math:`K` je faktor erodovatelnosti půdy, vyjádřený v závislosti na
  textuře a struktuře ornice, obsahu organické hmoty v ornici a
  propustnosti půdního profilu
* :math:`L` je faktor délky svahu, vyjadřující vliv nepřerušené délky
  svahu na velkost ztráty půdy erozí
* :math:`S` je faktor sklonu svahu
* :math:`C` je faktor ochranného vlivu vegetačního pokryvu, vyjádřený
  v závislosti na vývoji vegetace a použité agrotechnice
* :math:`P` je faktor účinnosti protierozních opatření

Jak je patrné z rovnice :eq:`usle`, je problém eroze půdy komplexním
jevem, zahrnující hydrologické charakteristiky, půdní vlastnosti,
topografii, vliv vegetace a agrotechnických a dalších
protierozních opatření. Model použitý v programu RadAgro je do jisté
míry zjednodušený, s ohledem na výpočetní možnosti a uživatelskou
náročnost při přípravě a zadávání dat do programu. Výpočet
jednotlivých faktorů rovnice USLE je uveden v dalším textu.
Podrobnosti k erozní ohroženosti půd a způsobu hodnocení pomocí
rovnice USLE vádí Janeček akol. (2012).


Faktor R
---------

Faktor :math:`R` představuje míru erozní účinnosti dešťů. Hodnota je
vyjádřena v závislosti na kinetické energii, úhrnu a intenzitě erozně
nebezpečných dešťů. Pro území České republiky se jako průměrná
doporučuje hodnota :math:`R=40`. Protože v průběhu roku dochází ke
změnám erozního ohrožení půd vlivem deště, je pravděpodobnost úrovně
faktoru :math:`R` rozdělena po jednotlivých měsících. Průměrnou
hodnotu :math:`R` i její procentické rozdělení v průběhu roku lze
nastavit v uživatelském rozhraní programu RadAgro.

Faktor K
---------

Faktor :math:`K` je mírou erodovatelnosti půdy. Hodnota faktoru je
vyjádřena v závislosti na textuře a struktuře ornice, obsahu
organické hmoty v ornici a propustnosti půdního profilu. Program
RadAgro definuje hodnoty faktoru K v závislosti na hlavní půdní
jednotce. Hodnoty faktoru K pro HPJ uvádí následující tabulka.

.. csv-table:: Přehled hodnot faktoru :math:`K` pro kategorie HPJ.
    :header: "HPJ",	"K faktor",	"HPJ", "K faktor", "HPJ", "K faktor"

    1,0.41,27,0.34,53,0.38
    2,0.46,28,0.29,54,0.4
    3,0.35,29,0.32,55,0.25
    4,0.16,30,0.23,56,0.4
    5,0.28,31,0.16,57,0.45
    6,0.32,32,0.19,58,0.42
    7,0.26,33,0.31,59,0.35
    8,0.49,34,0.26,60,0.31
    9,0.6,35,0.36,61,0.32
    10,0.53,36,0.26,62,0.35
    11,0.52,37,0.16,63,0.31
    12,0.5,38,0.31,64,0.4
    13,0.54,39,NA,65,NA
    14,0.59,40,0.24,66,NA
    15,0.51,41,0.33,67,0.44
    16,0.51,42,0.56,68,0.49
    17,0.4,43,0.58,69,NA
    18,0.24,44,0.56,70,0.41
    19,0.33,45,0.54,71,0.47
    20,0.28,46,0.47,72,0.48
    21,0.15,47,0.43,73,0.48
    22,0.24,48,0.41,74,NA
    23,0.25,49,0.35,75,NA
    24,0.38,50,0.33,76,NA
    25,0.45,51,0.26,77,NA
    26,0.41,52,0.37,78,NA

V uživatelském rozhraní programu RadAgro jsou zobrazeny kategorie HPJ
přítomné v zájmovém území a odpovídající hodnoty :math:`K` faktoru.
Hodnoty lze upravovat podle potřeby.


Faktor L a S
--------------

Faktory :math:`L` a :math:`S` jsou faktory délky a sklonu svahu. V
obou případech je výpočet proveden na základě digitálního modelu
terénu (DMT). Pro účely programu RadAgro byl použit model výpočtu pro
erozní model RUSLE (Revisited Universal Soil Loss Equation), který
vychází z velikosti pixelu použité rastrové vrstvy a z
pravděpodobnostního modelu akumulace odtoku, viz rovnice :eq:`flowacc`
. Použit byl přístup výpočtu podle Mitášové et al. (1996) v
následných modifikacích, viz např. Neteler a Mitášová (2008).

Faktory :math:`L` a :math:`S` byly vypočteny následujícím způsobem:

.. math::
    :label: l_factor

    L = n \cdot \left(\frac{flowacc \cdot X}{22.1}\right)^m

a

.. math::
    :label: s_factor

    S = \sin \left(\frac{slope}{0.09}\right)^n

kde :math:`n` a :math:`m` jsou konstanty, :math:`flowacc` je
matice pavděpodobnosti odtoku vody vypočtená podle rovnice
:eq:`flowacc`, X je velikost pixelu v metrech a :math:`slope` je
sklonitost terénu (°). Hodnoty konstant lze upravit v uživatelském
rozhraní programu RadAgro.


Faktor C
---------

Faktor ochranného vlivu vegetačního pokryvu :math:`C` zahrnuje
problematiku vývoje vegetačního krytu a použité agrotechniky. Z
důvodu značné komplikovanosti stanovení faktoru C v rámci erozního
modelu byly použity konstantní hodnoty pro jednotlivé plodiny a
další kategorie krajinného pokryvu uváděné Janečkem a kol (2012). Pro
jednotlivé plodiny jsou hodnoty uvedeny v následující tabulce.

.. csv-table:: Přehled hodnot faktoru :math:`C` pro jednotlivé plodiny a další kategorie krajinného pokryvu.
    :header: Plodina,C faktor,Plodina,C faktor

    Pšenice ozimá,0.12,Ostatní pícniny víceleté,0.01
    Pšenice jarní,0.15,Řepka ozimá,0.22
    Žito ozimé,0.17,Slunečnice,0.6
    Tritikale,0.17,Mák,0.5
    Ječmen jarní,0.15,Ostatní olejniny,0.22
    Ječmen ozimý,0.17,Trvalé travní porosty,0.005
    Oves,0.1,Pastviny,0.005
    Kukuřice na zrno,0.61,Chmel,0.8
    Kukuřice na siláž,0.72,Zelenina,0.45
    Čirok,0.72,Sady,0.45
    Brambory rané,0.6,Lesy,0.001
    Brambory pozdní,0.44,Zástavba,0.8
    Luštěniny,0.05,Ostatní kultury,0.9
    Jeteloviny,0.01,Ostatní plochy,0.9
    Ostatní pícniny jednoleté,0.02,,

Hodnoty faktoru :math:`C` lze upravovat v uživatelském prostředí
programu RadAgro.


Faktor P
---------

Faktor :math:`P` představuje míru účinnosti protierozních opatření.
Pro účely programu RadAgro byla zvolena konstantní hodnota pro celé
zájmové území, kterou lze upravit přímo v uživatelském rozhraní
programu.


Přenos radioaktivní kontaminace v biomase
=========================================

V biomase rostlin dochází v průběhu jejich života k akumulaci
radionuklidů. Množství kontaminantu, který je akumulován rostlinou
závisí na mnoha faktorech, jako je druh rostliny, její fyziologická
kondice, půdní prostředí, vodní režim apod. Pro účely programu
RadAgro byl pro výpočet akumulace radionuklidu v biomase rostlin
použit jednoduchý přístup, který předpokládá homogenní akumulaci
radionuklidu v jednotlivých druzích rostlin, bez ohledu na půdní
prostředí a další faktory. Relativní míra akumulace radionuklidu v
rostlině je vyjádřena specifickým transferovým koeficientem
:math:`T_k \ (m^{2}\cdot kg^{-1})` pro konkrétní radionuklid. Měrná
aktivita porostu :math:`(A_p; \ Bq.kg^{-1})` je součinem celkové měrné
aktivity :math:`(A_t; \ Bq.m^{-2})` a transferového koeficientu:

.. math::
    :label: activity_biomass

    A_p=T_k \cdot A_t

Snížení celkové měrné aktivity plochy na základě odstranění biomasy
porostů při sklizni je vypočteno se zahrnutím sušiny nadzemní biomasy
rostlin vypočtené pro termín sklizně konkrétní plodiny:

.. math::
    :label: activity_out

    A_{t[i+1]} = A_{t[i]} - A_{p[i]} D_{w[i]}

kde :math:`Dw` je sušina dané plodiny v :math:`kg.m^{-2}` a :math:`i`
je označení časového kroku.

Schéma výpočtu ukazuje obrázek:

.. image:: figs/models/schema_radiotransfer.png
    :align: center

Hodnoty transferových koeficientů shrnuje tabulka.

.. csv-table:: Přehled hodnot transferových koeficientů pro jednotlivé plodiny a další kategorie krajinného pokryvu pro cesium 137 a stroncium 90.
    :header: Plodina,TK 137Cs,TK 90Sr,Plodina,TK 137Cs,TK 90Sr

    Pšenice ozimá,0.15,1.1,Luštěniny,0.04,1.4
    Pšenice jarní,0.15,1.1,Jeteloviny,0.04,1.4
    Žito ozimé,0.15,1.1,Ostatní pícniny jednoleté,0.25,1.3
    Tritikale,0.15,1.1,Ostatní pícniny víceleté,0.25,1.3
    Ječmen jarní,0.15,1.1,Řepka ozimá,0.31,0.88
    Ječmen ozimý,0.15,1.1,Slunečnice,0.31,0.88
    Oves,0.15,1.1,Mák,0.31,0.88
    Kukuřice na zrno,0.073,0.73,Ostatní olejniny,0.31,0.88
    Kukuřice na siláž,0.073,0.73,Trvalé travní porosty,0.063,0.91
    Čirok,0.073,0.73,Pastviny,0.063,0.91
    Brambory rané,0.056,0.16,Chmel,0.31,0.88
    Brambory pozdní,0.056,0.16,Zelenina,0.06,0.76


Radioaktivní přeměna
=====================

Model radioaktivního rozpadu radionuklidu vychází z poločasu
radioaktivního rozpadu pro daný radionuklid. Radioaktivní rozpad je
pro daný časový integrál stanoven podle vztahu:

.. math::
    :label: halflife

    A = A_0 \mathrm{e}^{-\lambda t}

kde :math:`A` je konečná aktivita :math:`(Bq.m-2)`, :math:`A_0` je
počáteční aktivita :math:`(Bq.m-2)`, :math:`\lambda` je přeměnová
konstanta :math:`(s^{-1})` a :math:`t` je čas :math:`(s)`.


Referenční úrovně kontaminace biomasy
=======================================

Území kontaminované radioaktivní depozicí je pro praktické účely rozděleno na
tři oblasti, v závislosti na stanovených referenčních úrovních. Rozdělení
sledovaného území do oblastí podle referenčních úrovní vychází z předpokladu,
že lze vymezit území, ve kterých kontaminace nepřekračuje stanovenou úroveň
dávkového příkonu nebezpečného pro obyvatelstvo a zvířata (hodnota 0), dále
území ve kterých lze provádět opatření za účelem radiační ochrany (hodnota 1)
a území, kde úroveň radioaktivní kontaminace, respektive dávkového příkonu
překračuje bezpečnou hranici pro další management (hodnota 2).
Pro referenční úrovně RU 0 a RU 2 není doporučeno odstranění biomasy za
účelem ochrany půdy. V prvním případě (RU 0) nepřesahuje kontaminace
stanovenou mez a nejsou ze předpokládána další rizika, zeleň a produkci
rostlinné biomasy je možné využít běžným způsobem, případně v omezené míře na
základě dalších postupů. Naopak v případě ploch zařazených do referenční
úrovně RU 2 existuje předpoklad nadlimitní radioaktivní kontaminace ploch a
možnost ohrožení zdraví pracovníků pověřených manipulací s nadzemní biomasou
rostlin. V rámci ploch zařazených do RU 1 lze předpokládat půdoochranný
význam vegetačního krytu, který lze za daných podmínek odstranit z půdního
povrchu. Limitem je zde množství živé nadzemní biomasy 0,5 :math:`t.ha^{-1}`,
kdy předpokládáme, že sklizeň menšího množství biomasy na danou plochu je již
neefektivní, případně technicky nemožná. Hranice referenčních úrovní lze
nastavit přímo v uživatelském rozhraní programu. Přednastaveny jsou
hodnoty 5000 :math:`Bq.m^{-2}` a 3 :math:`MBq.m^{-2}`.

Území je rozděleno do skupin podle referenčních úrovní kontaminace
též v dlouhodobé předpovědi, kdy je území rozděleno do skupin pro
každý časový interval výpočtu (měsíc).
