#ETL Microdados do INEP = Educação Superior
#Autor: Kaique Fernandes
#Data: 18/11/2023

#Conectar na base do DW_INEP
import mysql.connector
import pandas as pd

#Dictionary com a config do banco para conexão
config = {
    'user':'root',
    'password':'1234',
    'host': 'localhost',
    'database':'dw_inep',
    'port': '3306'
}
try:
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()

    #MICRODADOS_CADASTRO_CURSOS_2020.CSV
    dados_2020 = pd.read_csv('C:/Users/Kaique.Fernandes/Documents/GitHub/DataScience/Etl_Atv1/Docs/microdados_censo_da_educacao_superior_2020/dados/MICRODADOS_CADASTRO_CURSOS_2020.CSV'
                        ,sep=';'
                        ,encoding='iso-8859-1'
                        ,low_memory=False)
    dados_2020 = dados_2020.fillna('')
    
    #MICRODADOS_CADASTRO_CURSOS_2021.CSV
    dados_2021 = pd.read_csv('C:/Users/Kaique.Fernandes/Documents/GitHub/DataScience/Etl_Atv1/Docs/microdados_censo_da_educacao_superior_2021/dados/MICRODADOS_CADASTRO_CURSOS_2021.CSV'
                        ,sep=';'
                        ,encoding='iso-8859-1'
                        ,low_memory=False)
    dados_2021 = dados_2021.fillna('')
    
    
    #UF
    dados_uf = pd.DataFrame(dados_2020['NO_UF'].unique(), columns = ['uf'])
    
    for i, r in dados_uf.iterrows():
        insert_statement = 'insert into dim_uf (tf_uf, uf) values (' \
                            + str(i) +',\'' \
                            + str(r['uf']) +'\')'
        print(insert_statement)
        cursor.execute(insert_statement)
        conn.commit()
    
    #Municipio 2020
    dados_municipio = pd.DataFrame(dados_2020['NO_MUNICIPIO'].unique(), columns = ['Municipio'])

    for i,r in dados_municipio.iterrows():
        municipio = r['Municipio']
        municipio = municipio.replace("'","")
        insert_statement = f"insert into dim_municipio (tf_municipio, municipio) values({i}, '{municipio}')"
        print(insert_statement)
        cursor.execute(insert_statement)
        conn.commit()
        
        
    #Municipio 2021
    dados_municipio = pd.DataFrame(dados_2021['NO_MUNICIPIO'].unique(), columns=['Municipio'])

    for i, r in dados_municipio.iterrows():
        municipio = r['Municipio'].replace("'", "")

        # Verifica se o município já existe no banco de dados
        check_query = f'SELECT COUNT(*) FROM dim_municipio WHERE municipio = "' + str({municipio}) +'"'
        cursor.execute(check_query)
        result = cursor.fetchone()

        # Se o município não existe, faz a inserção
        if result[0] == 0:
            insert_statement = f'INSERT INTO dim_municipio (tf_municipio, municipio) VALUES ({i}, " ' + str({municipio}) + '")'
            cursor.execute(insert_statement)
            conn.commit()
            print(f"Municipio '{municipio}' inserido com sucesso")
        else:
            print(f"O município '{municipio}' já existe no banco de dados.")
        
        
    #modalidade ensino
    dados_modalidade = pd.DataFrame(dados_2020['TP_MODALIDADE_ENSINO'].unique(), columns = ['tp_modalidade_ensino'])
    
    for i,r in dados_modalidade.iterrows():
        if r['tp_modalidade_ensino'] == 1:
            insert_statement = f"insert into dim_modalidade (tf_modalidade, modalidade) values({r['tp_modalidade_ensino']}, 'Presencial')"
        elif  r['tp_modalidade_ensino'] == 2:
            insert_statement = f"insert into dim_modalidade (tf_modalidade, modalidade) values({r['tp_modalidade_ensino']}, 'EAD')"
        cursor.execute(insert_statement)
        conn.commit()
    
    
    #CURSO
    dados_curso = pd.DataFrame(dados_2021['NO_CURSO'].unique(), columns = ['curso'])
    for i,r in dados_curso.iterrows():
        insert_statement = f"insert into dim_curso (tf_curso, curso) values({i+1}, '{r['curso']}')"
        cursor.execute(insert_statement)
        conn.commit()
    
    
    #ano 2020
    dados_ano= pd.DataFrame(dados_2020['NU_ANO_CENSO'].unique(), columns = ['ano'])
    for i,r in dados_ano.iterrows():
        insert_statement = f"insert into dim_ano (tf_ano, ano) values({i+1}, '{r['ano']}')"
        cursor.execute(insert_statement)
        conn.commit()
        
        
    #ano 2021
    dados_ano= pd.DataFrame(dados_2021['NU_ANO_CENSO'].unique(), columns = ['ano'])
    for i,r in dados_ano.iterrows():
        insert_statement = f"insert into dim_ano (tf_ano, ano) values({i+1}, '{r['ano']}')"
        cursor.execute(insert_statement)
        conn.commit()
        
        
        
    #IES 2020
    dados_IES_2020 = pd.read_csv('C:/Users/Kaique.Fernandes/Documents/GitHub/DataScience/Etl_Atv1/Docs/microdados_censo_da_educacao_superior_2020/dados/MICRODADOS_CADASTRO_IES_2020.CSV'
                    ,sep=';'
                    ,encoding='iso-8859-1'
                    ,low_memory=False)
    dados_IES_2020 = dados_IES_2020[['CO_IES','NO_IES']]
    

    dados_IES_curso = pd.DataFrame(dados_2020['CO_IES'].unique(), columns = ['co_ies'])
    for i, r in dados_IES_curso.iterrows():
        #determinar o nome da ies
        dados_IES_filtrado=dados_IES_2020[dados_IES_2020['CO_IES'] == r['co_ies']]
        no_ies = dados_IES_filtrado['NO_IES'].iloc[0].replace("'","")
        insert_statement = f"insert into dim_ies (tf_ies, ies) values({i+1}, '{no_ies}')"
        cursor.execute(insert_statement)
        conn.commit()
        
        

    #Fact matriculas 2020
    for i, r in dados_2020.iterrows():
        if r['TP_MODALIDADE_ENSINO'] == 1:
            modalidade = 'Presencial'
        elif r['TP_MODALIDADE_ENSINO'] == 2:
            modalidade = 'EAD'

        tf_uf_select_statement= f"select tf_uf from dim_uf where uf ='{r['NO_UF']}'" if r['NO_UF'] else "select Null from dim_uf"
        tf_municipio_select_statement= f"select tf_municipio from dim_municipio where municipio = " + {r['NO_MUNICIPIO']} +'"' if r['NO_MUNICIPIO'] else "select Null from dim_municipio"

        dados_IES_filtrado=dados_IES_2020[dados_IES_2020['CO_IES'] == r['CO_IES']]
        no_ies = dados_IES_filtrado['NO_IES'].iloc[0].replace("'","")

        insert_statement = f"""insert into fact_matriculas(matriculas,tf_ano,tf_curso,tf_ies,tf_uf,tf_municipio,tf_modalidade)
        select distinct * from 
        (select {r['QT_INSCRITO_TOTAL']}) as matriculas,
        (select tf_ano from dim_ano where ano = {r['NU_ANO_CENSO']}) as tf_ano,
        (select tf_curso from dim_curso where curso = '{r['NO_CURSO']}') as tf_curso,
        (select tf_ies from dim_ies where ies = '{no_ies}') as tf_ies,
        ({tf_uf_select_statement}) as tf_uf,
        ({tf_municipio_select_statement}) as tf_municipio,
        (select tf_modalidade from dim_modalidade where modalidade = '{modalidade}') as tf_modalidade
        """
        print(insert_statement)
        cursor.execute(insert_statement)
        conn.commit()
        
        
        
    #IES 2021
    dados_IES_2021 = pd.read_csv('C:/Users/Kaique.Fernandes/Documents/GitHub/DataScience/Etl_Atv1/Docs/microdados_censo_da_educacao_superior_2020/dados/MICRODADOS_CADASTRO_IES_2021.CSV'
                    ,sep=';'
                    ,encoding='iso-8859-1'
                    ,low_memory=False)
    dados_IES_2021 = dados_IES_2021[['CO_IES','NO_IES']]
    
    dados_IES_curso = pd.DataFrame(dados_2021['CO_IES'].unique(), columns = ['co_ies'])
    for i, r in dados_IES_curso.iterrows():
        #determinar o nome da ies
        dados_IES_filtrado=dados_IES_2021[dados_IES_2021['CO_IES'] == r['co_ies']]
        no_ies = dados_IES_filtrado['NO_IES'].iloc[0].replace("'","")
        insert_statement = f"insert into dim_ies (tf_ies, ies) values({i+1}, '{no_ies}')"
        cursor.execute(insert_statement)
        conn.commit()
        
        
        
    #Fact matriculas 2021
    for i, r in dados_2021.iterrows():
        if r['TP_MODALIDADE_ENSINO'] == 1:
            modalidade = 'Presencial'
        elif r['TP_MODALIDADE_ENSINO'] == 2:
            modalidade = 'EAD'

        tf_uf_select_statement= f"select tf_uf from dim_uf where uf ='{r['NO_UF']}'" if r['NO_UF'] else "select Null from dim_uf"
        tf_municipio_select_statement= f"select tf_municipio from dim_municipio where municipio = '{r['NO_MUNICIPIO']}'" if r['NO_MUNICIPIO'] else "select Null from dim_municipio"

        dados_IES_filtrado=dados_IES_2021[dados_IES_2021['CO_IES'] == r['CO_IES']]
        no_ies = dados_IES_filtrado['NO_IES'].iloc[0].replace("'","")

        insert_statement = f"""insert into fact_matriculas(matriculas,tf_ano,tf_curso,tf_ies,tf_uf,tf_municipio,tf_modalidade)
        select distinct * from 
        (select {r['QT_INSCRITO_TOTAL']}) as matriculas,
        (select tf_ano from dim_ano where ano = {r['NU_ANO_CENSO']}) as tf_ano,
        (select tf_curso from dim_curso where curso = '{r['NO_CURSO']}') as tf_curso,
        (select tf_ies from dim_ies where ies = '{no_ies}') as tf_ies,
        ({tf_uf_select_statement}) as tf_uf,
        ({tf_municipio_select_statement}) as tf_municipio,
        (select tf_modalidade from dim_modalidade where modalidade = '{modalidade}') as tf_modalidade
        """
       # print(insert_statement)
        cursor.execute(insert_statement)
        conn.commit()
        
    print('Acabou!')

except Exception as e:
    print(e)