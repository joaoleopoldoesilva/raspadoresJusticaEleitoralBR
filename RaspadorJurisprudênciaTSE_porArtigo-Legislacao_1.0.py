""" :: Raspador de acórdãos do TSE ::
    Raspa o site de pesquisa da jurisprudência do TSE, baixando todos os acórdãos dentro
    de parâmetros definidos: período de decisões e artigos de legislação relevante.

    Depente do webdriver Gecko, e do módulo selenium (pip install selenium).
"""

""" módulos para importação """
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
import time, os, re, datetime

def raiz():
    raiz = "C:\\Users\\matheus\\Documents\\TEST\\10"
    return raiz

if not os.path.isdir(raiz()):
    os.makedirs(raiz())
t00 = datetime.datetime.now()
siglasTribunais = ("TSE","TRE-AC","TRE-AL","TRE-AM","TRE-AP","TRE-BA","TRE-CE","TRE-DF","TRE-ES","TRE-GO","TRE-MA","TRE-MT","TRE-MS","TRE-MG","TRE-PA","TRE-PB","TRE-PR","TRE-PE","TRE-PI","TRE-RJ","TRE-RN","TRE-RS","TRE-RO","TRE-RR","TRE-SC","TRE-SP","TRE-SE","TRE-TO")
dicioTribunais = {'TSE': 0, 'TRE-AC': 1, 'TRE-AL': 2, 'TRE-AM': 3, 'TRE-AP': 4, 'TRE-BA': 5, 'TRE-CE': 6, 'TRE-DF': 7, 'TRE-ES': 8, 'TRE-GO': 9, 'TRE-MA': 10, 'TRE-MT': 11, 'TRE-MS': 12, 'TRE-MG': 13, 'TRE-PA': 14, 'TRE-PB': 15, 'TRE-PR': 16, 'TRE-PE': 17, 'TRE-PI': 18, 'TRE-RJ': 19, 'TRE-RN': 20, 'TRE-RS': 21, 'TRE-RO': 22, 'TRE-RR': 23, 'TRE-SC': 24, 'TRE-SP': 25, 'TRE-SE': 26, 'TRE-TO': 27}


def robôLogger(modo, txt1, txt2=None): ## talvez escrever modo para loggar tempo
    if modo == 1:
        with open(loggerPath(), 'a') as f:
            f.write(listaClasses[txt1].upper()+'\t'+listaAssuntos[txt2].capitalize()+'\n')
    if modo == 2:
        with open(loggerPath(), 'a') as f:
            f.write('\t%s\t%s\n' % (txt1, txt2))
    if modo == 3:
        with open(loggerPath(), 'a') as f:
            f.write(txt1+'\t'+txt2)
    if modo == 4:
        with open(loggerPath(), 'a') as f:
            log = "%s %s/%s\tArtigo %s\n" % (txt1[0], txt1[2], txt1[3][-2:], str(txt2))
            f.write(log)

def conversorTempo(t): ## está muito ruim essa solução, precisa limpar
    tempo = str(t.year)[2:]+'-'+str(t.month).zfill(2)+'-'+str(t.day).zfill(2)+'_'+str(t.hour).zfill(2)+'-'+str(t.minute).zfill(2)+'-'+str(t.second).zfill(2)
    return tempo


""" Parâmetros de busca """
def dataInicio():
    dataInicio = input("Insira o dia em que começa o período desejado de busca no formato dd/mm/aaaa:")
    while re.fullmatch(r'(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[012])/(19[3-9]\d|20[0-3]\d)', dataInicio) == None:
        print("Por favor, utilize o formato dd/mm/aaaa (e.x. 01/01/1995)")
        dataInicio = input("Insira o dia em que começa o período desejado de busca no formato dd/mm/aaaa:")
    robôLogger(3, "Período:", "de %s a " % dataInicio)
    return dataInicio.replace("/", "%2F")

def dataFim():
    dataFim = input("Insira o dia em que termina o período desejado de busca no formato dd/mm/aaaa:")
    while re.fullmatch(r'(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[012])/(19[3-9]\d|20[0-3]\d)', dataFim) == None:
        print("Por favor, utilize o formato dd/mm/aaaa (e.x. 01/01/1995)")
        dataFim = input("Insira o dia em que termina o período desejado de busca no formato dd/mm/aaaa:")
    robôLogger(3, '%s.' % dataFim, '\n')
    return dataFim.replace("/", "%2F")

def listaTribunais(siglasTribunais=siglasTribunais, dicioTribunais=dicioTribunais):
    listaTribunais = []
    tribunal = input("Insira a sigla de um tribunal que deseja incluir nos parâmetros de busca (por exemplo TSE, ou TRE-AL, etc.):").upper()
    if tribunal == "TODOS":
        listaTribunaisOrdenada = ["TSE","TRE-AC","TRE-AL","TRE-AM","TRE-AP","TRE-BA","TRE-CE","TRE-DF","TRE-ES","TRE-GO","TRE-MA","TRE-MT","TRE-MS","TRE-MG","TRE-PA","TRE-PB","TRE-PR","TRE-PE","TRE-PI","TRE-RJ","TRE-RN","TRE-RS","TRE-RO","TRE-RR","TRE-SC","TRE-SP","TRE-SE","TRE-TO"]
    else:
        while tribunal not in siglasTribunais:
            tribunal = input("Você inseriu um termo inválido: '%s'. Insira a sigla de um tribunal que deseja incluir nos parâmetros de busca, utilizando apenas maiúsculas, e sem espaços (por exemplo TSE, ou TRE-AL, etc.):" % tribunal).upper()
        listaTribunais.append(tribunal)
        tribunal = input("Você pode incluir mais de 1 tribunal na sua busca (por exemplo TSE, ou TRE-AL, etc.). Se você não quer incluir mais tribunais, apenas tecle ENTER:").upper()
        while tribunal != "" and tribunal != "ENTER":
            if tribunal not in siglasTribunais:
                tribunal = input("Você inseriu um termo inválido: '%s'. Insira a sigla de um tribunal que deseja incluir nos parâmetros de busca, utilizando apenas maiúsculas, e sem espaços (por exemplo TSE, ou TRE-AL, etc.). Se você não quer incluir mais tribunais, apenas tecle ENTER:" % tribunal).upper()
            else:
                listaTribunais.append(tribunal)
                tribunal = input("Você pode incluir mais de 1 tribunal na sua busca (por exemplo TSE, ou TRE-AL, etc.). Se você não quer incluir mais tribunais, apenas tecle ENTER:").upper()
        listaTribunais_duplas = []
        for siglaTribunal in listaTribunais:
            listaTribunais_duplas.append((siglaTribunal, dicioTribunais[siglaTribunal]))
        listaTribunais_duplas.sort(key=lambda s: s[1])
        listaTribunaisOrdenada = []
        for dupla in listaTribunais_duplas:
            listaTribunaisOrdenada.append(dupla[0])
        robôLogger(3, "Tribunais:", str(listaTribunaisOrdenada).strip('[]')+'.\n')
    return listaTribunaisOrdenada

def legislaçãoRelevante():
    legislação = input("Insira a legislação de referência que deseja incluir como parâmetro de busca, no formato No-da-lei/aaaa (por exemplo, para o código eleitoral: 4737/1965):")
    while re.fullmatch(r'\d+/\d{4}', legislação) == None:
        print("Por favor, utilize o fomato lei/aaaa")
        legislação = input("Insira a legislação de referência que deseja incluir como parâmetro de busca, no formato lei/aaaa (por exemplo, para o código eleitoral: 4737/1965):")
    numLei, anoLei = legislação.split("/")
    siglaLei = input("Insira LEI, se for uma lei ordinária, ou LC, se for uma lei complementar:").upper()
    while siglaLei not in ("LEI", "LC"):
        siglaLei = input("Por favor, insira LEI, se for uma lei ordinária, ou LC, se for uma lei complementar:").upper()
    if siglaLei == "LEI":
        descriçãoLei = "LEI+ORDINARIA"
    else:
        descriçãoLei = "LEI+COMPLEMENTAR"
    referênciaLegislativa = [siglaLei, descriçãoLei, numLei, anoLei]
    listaReferênciasLegislativas = ['',]
    listaReferênciasLegislativas[0] = referênciaLegislativa
    artigosReferênciaLegislativa = ['',]
    listaArtigos = ['',]
    artigoBusca = input("Se quiser refinar a pesquisa dessa legislação para um artigo específico, insira aqui, senão tecle ENTER:").lower()
    if artigoBusca == "" or artigoBusca.upper() == "ENTER":
        artigoBusca = None
        pass
    else:   #se não é vazio
        while artigoBusca != "" and artigoBusca.upper() != "ENTER" and re.fullmatch(r'\d{1,5}[a-z]?', artigoBusca) == None: # se for inválido
            print("Você inseriu um artigo inválido, artigos só podem conter números e até 1 letra ao final, tente novamente.")
            artigoBusca = input("Se quiser refinar a pesquisa dessa legislação para um artigo específico, insira aqui, senão tecle ENTER:").lower()
        if artigoBusca != "" and artigoBusca.upper() != "ENTER": # se for válido e não-vazio
            listaArtigos[0] = artigoBusca
            while artigoBusca != "" and artigoBusca.upper() != "ENTER":
                artigoBusca = input("Você pode inserir mais de 1 artigo referente a essa legislação na sua busca, inserindo-os 1 de cada vez, aqui (se não quiser incluir mais artigos, apenas tecle ENTER):").lower()
                while artigoBusca != "" and artigoBusca.upper() != "ENTER" and re.fullmatch(r'\d{1,5}[a-z]?', artigoBusca) == None:
                    print("Você inseriu um artigo inválido, artigos só podem conter números e até 1 letra ao final, tente novamente.")
                    artigoBusca = input("Se quiser refinar a pesquisa dessa legislação para um artigo específico, insira aqui, senão tecle ENTER:").lower()
                if artigoBusca == "" and artigoBusca.upper() == "ENTER":
                    artigoBusca = None
                    break
                else:
                    listaArtigos.append(artigoBusca)
    if len(listaArtigos) > 1:
        listaArtigos.pop()
    artigosReferênciaLegislativa[0] = listaArtigos
    legislação = input("Você pode inserir mais de 1 legislação como parâmetro de busca, no mesmo formato (lei/aaaa). Se você não quer incluir mais nenhuma legislação como parâmetro de busca, apenas tecle ENTER:")
    while legislação != "" and legislação != "ENTER":
        while legislação != "" and legislação != "ENTER" and re.fullmatch(r'\d+/\d{4}', legislação) == None:
            print("Por favor, utilize o fomato lei/aaaa")
            legislação = input("Insira a legislação de referência que deseja incluir como parâmetro de busca, no formato lei/aaaa (por exemplo, para o código eleitoral: 4737/1965):")
        if legislação == "" and legislação == "ENTER":
            break
        numLei, anoLei = legislação.split("/")
        siglaLei = input("Insira LEI, se for uma lei ordinária, ou LC, se for uma lei complementar:").upper()
        while siglaLei not in ("LEI", "LC"):
            siglaLei = input("Por favor, insira LEI, se for uma lei ordinária, ou LC, se for uma lei complementar:").upper()
        if siglaLei == "LEI":
            descriçãoLei = "LEI+ORDINARIA"
        else:
            descriçãoLei = "LEI+COMPLEMENTAR"
        referênciaLegislativa = [siglaLei, descriçãoLei, numLei, anoLei]
        listaReferênciasLegislativas.append(referênciaLegislativa)
        listaArtigos = ['',]
        artigoBusca = input("Se quiser refinar a pesquisa dessa legislação para um artigo específico, insira aqui, senão tecle ENTER:").lower()
        if artigoBusca == "" or artigoBusca.upper() == "ENTER":
            artigoBusca = None
            pass
        else:   #se não é vazio
            while artigoBusca != "" and artigoBusca.upper() != "ENTER" and re.fullmatch(r'\d{1,5}[a-z]?', artigoBusca) == None: # se for inválido
                print("Você inseriu um artigo inválido, artigos só podem conter números e até 1 letra ao final, tente novamente.")
                artigoBusca = input("Se quiser refinar a pesquisa dessa legislação para um artigo específico, insira aqui, senão tecle ENTER:").lower()
            if artigoBusca != "" and artigoBusca.upper() != "ENTER": # se for válido e não-vazio
                listaArtigos[0] = artigoBusca
                while artigoBusca != "" and artigoBusca.upper() != "ENTER":
                    artigoBusca = input("Você pode inserir mais de 1 artigo referente a essa legislação na sua busca, inserindo-os 1 de cada vez, aqui (se não quiser incluir mais artigos, apenas tecle ENTER):").lower()
                    while artigoBusca != "" and artigoBusca.upper() != "ENTER" and re.fullmatch(r'\d{1,5}[a-z]?', artigoBusca) == None:
                        print("Você inseriu um artigo inválido, artigos só podem conter números e até 1 letra ao final, tente novamente.")
                        artigoBusca = input("Se quiser refinar a pesquisa dessa legislação para um artigo específico, insira aqui, senão tecle ENTER:").lower()
                    if artigoBusca == "" and artigoBusca.upper() == "ENTER":
                        artigoBusca = None
                        break
                    else:
                        listaArtigos.append(artigoBusca)
        if len(listaArtigos) > 1:
            listaArtigos.pop()
        artigosReferênciaLegislativa.append(listaArtigos)
        legislação = input("Você pode inserir mais de 1 legislação como parâmetro de busca, no mesmo formato (lei/aaaa). Se você não quer incluir mais nenhuma legislação como parâmetro de busca, apenas tecle ENTER:")
    with open(loggerPath(), 'a') as f:
        f.write("Legislação e artigos:\n")
        i = 0
        for lei in listaReferênciasLegislativas:
            printar = "%s_%s/%s" % (lei[0], lei[2], lei[3][-2:])
            f.write("\t%s\t%s\n" % (printar, artigosReferênciaLegislativa[i]))
            i+=1
        f.write("\n")
    return listaReferênciasLegislativas, artigosReferênciaLegislativa

def criaURLinicial(dataInicio, dataFim, listaTribunais, siglaLei, descriçãoLei, numLei, anoLei):
    stringTribunais = str()
    for tribunal in listaTribunais:
        if tribunal != 'TSE':
            stringTribunais += tribunal[-2:]+'%2C'
        else:
            stringTribunais += tribunal+'%2C'
    URL_inicial = "http://inter03.tse.jus.br/sjur-pesquisa/pesquisa/pagePesquisa.jsp?configName=SJUT&sectionServers="+stringTribunais[:-3]+"&threadGroupName=&sectionNameString=avancado&pageList=tocCompleto.jsp&toc=true&docIndexString=1&tipoAcordao=true&tipoResolucao=true&tipoDecisaoSemResolucao=true&tipoDecisaoMonocratica=false&livre=&tipoProcesso=&numeroProcesso=&classe=&parteAdv=&ufProcesso=&relator=&assunto=&numeroDecisao=&dataDecisaoInicio="+dataInicio+"&dataDecisaoFim="+dataFim+"&dataPubInicio=&dataPubFim=&uf=&refLegSigla=&refLegDescricao=&refLegNormaSigla="+siglaLei+"&refLegNormaDescricao="+descriçãoLei+"&refLegNormaNumero="+numLei+"&refLegNormaAno="+anoLei+"&refLegArtigoNumero=&refLegArtigoTipo1=&refLegArtigoTipoNumero1=&refLegArtigoTipo2=&refLegArtigoTipoNumero2=&refLegArtigoLetra=&refLegArtigoItem=&textoTodos=true&textoEmenta=true&textoDecisao=true&textoIndexacao=true&textoObservacao=true"
    return URL_inicial

def criaPath(tribunal, lei, artigo):
    legislação = "%s_%s-%s__" % (lei[0], lei[2], lei[3][-2:])
    if artigo != None:
        artigo = artigo.upper()
    path = os.path.join(raiz(), tribunal, legislação+artigo)
    if not os.path.isdir(path):
        os.makedirs(path)
    return path
    
def loggerPath(t=t00):
    loggerPath = os.path.join(raiz(), 'logRaspagem'+conversorTempo(t)+'.txt')
    return loggerPath


""" Configurações do navegador operado pelo robô, para fazer downloads automáticos ao clicar em botões, implementando uma solução para execuções em JavaScript"""
profile = FirefoxProfile()
profile.set_preference("browser.download.panel.shown", False)
profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/pdf, application/vnd.adobe.xfdf, application/vnd.fdf, application/vnd.adobe.xdp+xml, application/x-pdf, application/msword, application/vnd.openxmlformats-officedocument.wordprocessingml.document, application/vnd.ms-word.document.macroEnabled.12, application/x-download, image/tiff, application/force-download, application/vnd.oasis.opendocument.text, image/bmp, image/x-windows-bmp") ## completar a lista usando vírgulas
profile.set_preference("plugin.disable_full_page_plugin_for_types", "application/pdf, application/vnd.adobe.xfdf, application/vnd.fdf, application/vnd.adobe.xdp+xml, application/x-pdf, application/msword, application/vnd.openxmlformats-officedocument.wordprocessingml.document, application/vnd.ms-word.document.macroEnabled.12, application/x-download, image/tiff, application/force-download, application/vnd.oasis.opendocument.text, image/bmp, image/x-windows-bmp")
profile.set_preference("browser.download.folderList", 2);
profile.set_preference("browser.download.dir", raiz())
profile.set_preference("pdfjs.disabled", True)
profile.set_preference("browser.download.manager.showWhenStarting",False)
profile.set_preference("general.warnOnAboutConfig", False)
driver = webdriver.Firefox(firefox_profile=profile)

def set_string_preferce(name, value):
    modified = driver.execute_script("""
        document.getElementById("textbox").value = arguments[0];
        FilterPrefs();
        view.selection.currentIndex = 0;

        if (view.rowCount == 1) {
           current_value = view.getCellText(0, {id:"valeuCol"});
           if (current_value != arguments[1]) {
               ModifySelected();
               return true;
           }
        } 

        return false;
    """, name, value)
    if modified is None or modified is True:
        time.sleep(2)       ## precisa de um tempo aqui?
        alert = driver.switch_to.alert
        alert.send_keys(value)
        alert.accept()


def main(dataInicio, dataFim, listaTribunais, listaReferênciasLegislativas, artigosReferênciaLegislativa):
    nBusca, nRefLeg, nArtLeg = 0, 0, 0
    if 'TSE' in listaTribunais:
        w = 2
    else:
        w = 1
    for listaArtigos in artigosReferênciaLegislativa:
        nBusca += len(listaArtigos)
    print("iniciando %s buscas..." % nBusca)
    for i in range(nBusca):
        print("%s..." % str(i+1))
        nTribunal = 0
        robôLogger(4, listaReferênciasLegislativas[nRefLeg], artigosReferênciaLegislativa[nRefLeg][nArtLeg])
        driver.get(criaURLinicial(dataInicio, dataFim, listaTribunais, listaReferênciasLegislativas[nRefLeg][0], listaReferênciasLegislativas[nRefLeg][1], listaReferênciasLegislativas[nRefLeg][2], listaReferênciasLegislativas[nRefLeg][3]))
        driver.find_element_by_name("item1").send_keys(artigosReferênciaLegislativa[nRefLeg][nArtLeg])
        driver.find_element_by_name("submit").click()
        time.sleep(50)  ## como fazer uma espera mais inteligente? ...até não achar "Pesquisando..."
        tbodys = driver.find_elements_by_tag_name("tbody")
        trs = tbodys[2].find_elements_by_tag_name("tr")
        for tr in trs[w:]:
            try:
                tds = tr.find_elements_by_tag_name("td")
            except StaleElementReferenceException:
                tbodys = driver.find_elements_by_tag_name("tbody")
                trs = tbodys[2].find_elements_by_tag_name("tr")
                tds = trs[nTribunal+w].find_elements_by_tag_name("td")
                print("Erro percebido, StaleElementReferenceException. Na passagem '%s', %s %s/%s artigo '%s', tribunal '%s'. Linha 263." % (str(i+1), listaReferênciasLegislativas[nRefLeg][0], listaReferênciasLegislativas[nRefLeg][2], listaReferênciasLegislativas[nRefLeg][3], artigosReferênciaLegislativa[nRefLeg][nArtLeg], listaTribunais[nTribunal]))
            texto_td0, texto_td1 = tds[0].text.strip(), tds[1].text.strip()
            try:
                link_tribunal = tds[1].find_element_by_tag_name("a")
            except NoSuchElementException:
                robôLogger(2, texto_td0, texto_td1)
            else:
                link_tribunal.send_keys(Keys.CONTROL + Keys.RETURN)
                time.sleep(15)   ## como fazer uma espera mais inteligente?
                window_docs = driver.window_handles[1]
                driver.switch_to.window(window_docs)
                try:
                    driver.switch_to.window(driver.window_handles[2])
                except IndexError:
                    driver.find_element_by_link_text("Andamento processual").send_keys(Keys.CONTROL+Keys.RETURN)
                    time.sleep(10)
                    driver.switch_to.window(driver.window_handles[2])
                    driver.get("about:config")
                time.sleep(2)
                set_string_preferce("browser.download.dir", criaPath(listaTribunais[nTribunal], listaReferênciasLegislativas[nRefLeg], artigosReferênciaLegislativa[nRefLeg][nArtLeg]))
                driver.switch_to.window(window_docs)
                ha_prox_pag = True
                j=0
                while ha_prox_pag:
                    caixas = driver.find_elements_by_id("caixa")
                    for caixa in caixas:
                        j+=1
                        try:
                            InteiroTeor = caixa.find_element_by_link_text("Inteiro teor")
                        except StaleElementReferenceException:
                            print("Erro percebido, StaleElementReferenceException. Na passagem '%s', %s %s/%s artigo '%s', tribunal '%s', caixa '%s'. Linha 296." % (str(i+1), listaReferênciasLegislativas[nRefLeg][0], listaReferênciasLegislativas[nRefLeg][2], listaReferênciasLegislativas[nRefLeg][3], artigosReferênciaLegislativa[nRefLeg][nArtLeg], listaTribunais[nTribunal], str(j)))
                            return
                        InteiroTeor.click()
                        time.sleep(4)   ## como fazer uma espera mais inteligente?
                        driver.switch_to.window(window_docs)
                    try:
                        prox_pag = driver.find_element_by_link_text("Próxima >>")
                    except NoSuchElementException:
                        ha_prox_pag = False
                    else:
                        prox_pag.click()
                        time.sleep(30)   ## será que está faltando dar mais tempo?
                robôLogger(2, texto_td0, texto_td1)
                driver.close()
                driver.switch_to.window(driver.window_handles[0])   ## precisa de mais tempo?
            nTribunal+=1
        driver.find_element_by_link_text("Voltar").click()
        driver.find_element_by_name("livre").clear()
        if nArtLeg != len(artigosReferênciaLegislativa[nRefLeg])-1:
            nArtLeg+=1
        else:
            nRefLeg+=1
            nArtLeg=0
    time.sleep(450)
    driver.quit()
    print("\nBusca concluída!\n\n")


if __name__ == '__main__':
    robôLogger(3, '.::Parâmetros de busca::.', '\n')
    dataInicio = dataInicio()
    dataFim = dataFim()
    listaTribunais = listaTribunais()
    listaReferênciasLegislativas, artigosReferênciaLegislativa = legislaçãoRelevante()
    with open(loggerPath(), 'r') as f:
        print(f.read())
    robôLogger(3, '.::Log da busca::.', '\n')
    main(dataInicio, dataFim, listaTribunais, listaReferênciasLegislativas, artigosReferênciaLegislativa)
    with open(loggerPath(), 'r') as f:
        print(f.read())

""" Pendências do cógigo:
    - acrescentar funcionalidade de busca por classe e assunto
    - logar o tempo transcorrido na busca
    - criar esperas inteligentes para tornar o código mais eficiente
    - introduzir uma checagem dos documentos baixados
    - encontrar uma solução para os casos missing
    - melhorar a redação das mensagens de input
"""
