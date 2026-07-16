'''
==================================================================
 Práctica 3: Simulación Monte Carlo de desintegración nuclear
==================================================================

 AUTOR: Sofía Núñez de Andrés
 FECHA: 09/04/2026

 DESCRIPCIÓN:
 En esta práctica se simula la desintegración nuclear mediante
 métodos de Monte Carlo. Se modela el tiempo de vida de los
 núcleos como una variable aleatoria con distribución exponencial.
 
 Se estudian:
  - Desintegración simple
  - Cadena Bi -> Po -> Pb
  - Fotomultiplicador (Poisson)

 Se comparan los resultados con las soluciones teóricas y se
 analizan efectos estadísticos.

==================================================================
 FUNDAMENTO TEÓRICO
==================================================================

 La probabilidad de desintegración sigue una distribución:

     P(t) = (1/τ) * exp(-t/τ)

 donde τ es la vida media.

 Usando el método de la transformada inversa:

     t = -τ ln(u)       con u ∈ U(0,1)

 La ley de desintegración nuclear es:

     N(t) = N0 * exp(-t/τ)

 Para la cadena Bi -> Po -> Pb (ecuaciones de Bateman):

     N_Bi(t) = N0 * exp(-t/τ_Bi)
     N_Po(t) = N0 * τ_Po/(τ_Po - τ_Bi) * (exp(-t/τ_Bi) - exp(-t/τ_Po))
     N_Pb(t) = N0 - N_Bi(t) - N_Po(t)    [Pb-208 es estable]

 En el fotomultiplicador:
 el número de electrones sigue una distribución de Poisson:

     P(n) = (ν^n / n!) * exp(-ν)

==================================================================
 INSTRUCCIONES DE EJECUCIÓN
==================================================================

 Ejecutar en terminal:
 > python nombre_del_archivo.py

 El programa genera automáticamente:
  - Gráficas de desintegración
  - Ajustes exponenciales
  - Estudio de precisión estadística de tau
  - Cadena completa Bi -> Po -> Pb
  - Resultados del fotomultiplicador

'''
# Práctica 3: Simulación Monte Carlo de desintegración nuclear

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

print('\nInicio del programa: ')

# ============================================================
# FUNCIONES
# ============================================================

def exponencial(N, tau):
    """Genera N tiempos de desintegración con distribución exponencial
    mediante transformada inversa: t = -tau * ln(u), u aprox U(0,1)"""
    
    u = np.random.rand(N)
    
    return -tau * np.log(u)

def simulacion_desintegracion(N0, tau, t_max, pasos):
    """Simula la desintegración simple de N0 núcleos con vida media tau."""
    
    tiempos = exponencial(N0, tau)
    t = np.linspace(0, t_max, pasos)
    
    N_t = np.array([np.sum(tiempos > tiempo) for tiempo in t])
    
    return t, N_t

def teorico(t, N0, tau):
    """Solución teórica de la ley de desintegración."""
    
    return N0 * np.exp(-t / tau)

def poisson_manual(nu, n_muestras):
    """Genera n_muestras números de Poisson con parámetro nu
    usando el método del guión (producto de uniformes)."""
    resultados = []
    limite = np.exp(-nu)
    for _ in range(n_muestras):
        k = 1
        A = 1.0
        while True:
            A *= np.random.rand()
            if A < limite:
                resultados.append(k - 1)
                break
            k += 1
    return np.array(resultados)

# ============================================================
# CADENA Bi -> Po -> Pb  (Pb-208 es estable)
# ============================================================

def cadena_desintegracion(N0, tau_Bi, tau_Po, t_max, pasos):
    """
    Simula la cadena completa Bi-210 -> Po-210 -> Pb-208.
    Cada núcleo de Bi decae en un tiempo t_Bi aprox Exp(tau_Bi).
    Después, el Po resultante decae en un tiempo adicional t_Po aprox Exp(tau_Po).
    El Pb-208 es estable y se acumula indefinidamente.
    """
    
    tiempos_Bi = exponencial(N0, tau_Bi)
    tiempos_Po = tiempos_Bi + exponencial(N0, tau_Po)

    t = np.linspace(0, t_max, pasos)

    N_Bi = np.array([np.sum(tiempos_Bi > tiempo) for tiempo in t])
    N_Po = np.array([np.sum((tiempos_Bi <= tiempo) & (tiempos_Po > tiempo)) for tiempo in t])
    N_Pb = np.array([np.sum(tiempos_Po <= tiempo) for tiempo in t])

    return t, N_Bi, N_Po, N_Pb

def teorico_cadena(t, N0, tau_Bi, tau_Po):
    """
    Soluciones analíticas de Bateman para la cadena Bi -> Po -> Pb.
    """
    
    N_Bi = N0 * np.exp(-t / tau_Bi)
    N_Po = N0 * (1/(tau_Bi) / (1/(tau_Po) - 1/(tau_Bi))) * ( np.exp(-t / tau_Bi) - np.exp(-t / tau_Po) )
    
    return N_Bi, N_Po

# ============================================================
# FOTOMULTIPLICADOR
# ============================================================

def fotomultiplicador(n_dinodos=6, nu=5, n_fotones=1000, posicion_especial=None, nu_especial=7):
    """
    Simula un fotomultiplicador de n_dinodos dínodos con ganancia nu (Poisson).
    Si posicion_especial no es None, ese dínodo tiene ganancia nu_especial.
    Devuelve el array de electrones finales para cada fotón.
    """
    
    resultados = np.zeros(n_fotones, dtype=int)
    
    for k in range(n_fotones):
        electrones = 1
        
        for i in range(n_dinodos):
            nu_actual = nu_especial if i == posicion_especial else nu
            electrones = int(np.sum(np.random.poisson(nu_actual, size=electrones)))
        
        resultados[k] = electrones
    
    return resultados

# ============================================================
# PARÁMETROS GENERALES
# ============================================================

N0     = 10000
tau_Bi = 7.5       # días (vida media del Bi-210)
tau_Po = 190.0     # días (vida media del Po-210)

t_max1 = 1000      # para ver bien la cadena completa
t_max2 = 200       # para la desintegración simple del Bi
pasos  = 150

print("\n · Resultados de la simulación: ")

# ============================================================
# 1. DESINTEGRACIÓN SIMPLE + AJUSTE
# ============================================================
print('\n=====================================')
print("[1] DESINTEGRACIÓN NUCLEAR Y AJUSTE: ")
print('=====================================')

t, N_sim = simulacion_desintegracion(N0, tau_Bi, t_max2, pasos)

popt, _ = curve_fit(teorico, t, N_sim, p0=[N0, tau_Bi])
N0_fit, tau_fit = popt

print("\nAjuste exponencial (una simulación): ")
print(f" · Tau real       = {tau_Bi}")
print(f" · Tau ajustado   = {tau_fit:.4f}")
print(f" · N0 ajustado    = {N0_fit:.2f}")

plt.figure(figsize=(8,5))

plt.plot(t, N_sim, label="Simulación")
plt.plot(t, teorico(t, N0_fit, tau_fit), '--', label=f"Ajuste (τ={tau_fit:.3f})")
plt.plot(t, teorico(t, N0, tau_Bi), ':', color='gray', label=f"Teórico (τ={tau_Bi})")

plt.xlabel("Tiempo (días)")
plt.ylabel("N(t)")

plt.title("Desintegración nuclear del Bi-210")
plt.legend()

plt.grid(alpha=0.3)
plt.tight_layout()

plt.savefig("desintegracion.jpg", dpi=300, bbox_inches='tight')
plt.close()

# ============================================================
# 1b. REPETICIÓN DEL AJUSTE PARA ESTUDIO ESTADÍSTICO DE τ
# ============================================================
print('\n==================================================')
print("[1b] ESTUDIO ESTADÍSTICO DE LA ESTIMACIÓN DE tau")
print('==================================================')

n_repeticiones = 200
taus_estimados = []

for _ in range(n_repeticiones):
    t_rep, N_rep = simulacion_desintegracion(N0, tau_Bi, t_max2, pasos)
    
    try:
        popt_rep, _ = curve_fit(teorico, t_rep, N_rep, p0=[N0, tau_Bi])
        taus_estimados.append(popt_rep[1])
    
    except RuntimeError:
        pass  # descartamos ajustes que no convergen

taus_estimados = np.array(taus_estimados)
tau_media  = np.mean(taus_estimados)
tau_std    = np.std(taus_estimados)

print(f"\nRepetición del ajuste ({n_repeticiones} simulaciones):")
print(f" · Tau real          = {tau_Bi}")
print(f" · Tau medio         = {tau_media:.4f}")
print(f" · Desv. estándar    = {tau_std:.4f}")
print(f" · Error relativo    = {100*abs(tau_media - tau_Bi)/tau_Bi:.2f} %")

plt.figure(figsize=(8,5))

plt.hist(taus_estimados, bins=30, edgecolor='black', color='steelblue', alpha=0.8)

plt.axvline(tau_Bi,    color='red',    linestyle='--', label=f"τ real = {tau_Bi}")
plt.axvline(tau_media, color='orange', linestyle='-',  label=f"τ medio = {tau_media:.3f}")

plt.xlabel("τ estimado")
plt.ylabel("Frecuencia")

plt.title(f"Distribución de τ en {n_repeticiones} ajustes (N0={N0})")
plt.legend()

plt.grid(alpha=0.3)
plt.tight_layout()

plt.savefig("estudio_tau.jpg", dpi=300, bbox_inches='tight')
plt.close()

# Estudio de la precisión en función de N0
print('\n==============================================')
print("[1c] PRECISIÓN DE tau EN FUNCIÓN DE N0:")
print('==============================================')

N0_vals      = [500, 1000, 5000, 10000, 50000, 100000]
n_rep_prec   = 100
medias_tau   = []
std_tau      = []

for N_test in N0_vals:
    taus_tmp = []
    
    for _ in range(n_rep_prec):
        t_r, N_r = simulacion_desintegracion(N_test, tau_Bi, t_max2, pasos)
        
        try:
            p, _ = curve_fit(teorico, t_r, N_r, p0=[N_test, tau_Bi])
            taus_tmp.append(p[1])
        
        except RuntimeError:
            pass
    
    medias_tau.append(np.mean(taus_tmp))
    std_tau.append(np.std(taus_tmp))
    
    print(f"\n · N0 = {N_test:>7}  -> tau medio = {np.mean(taus_tmp):.3f}  ±  {np.std(taus_tmp):.4f}")

plt.figure(figsize=(8,5))

plt.errorbar(N0_vals, medias_tau, yerr=std_tau, fmt='o-', capsize=5, color='steelblue')
plt.axhline(tau_Bi, color='red', linestyle='--', label=f"τ real = {tau_Bi}")
plt.xscale('log')

plt.xlabel("N0 (escala log)")
plt.ylabel("τ estimado")

plt.title("Precisión de τ en función de N0")
plt.legend()

plt.grid(alpha=0.3)
plt.tight_layout()

plt.savefig("precision_tau.jpg", dpi=300, bbox_inches='tight')
plt.close()

# ============================================================
# 2. CADENA COMPLETA Bi -> Po -> Pb  (con curvas teóricas)
# ============================================================
print('\n====================================================')
print("[2] CADENA DE DESINTEGRACIÓN Bi -> Po -> Pb:  ")
print('====================================================')

t, N_Bi, N_Po, N_Pb = cadena_desintegracion(N0, tau_Bi, tau_Po, t_max1, pasos)  
N_Bi_teo, N_Po_teo = teorico_cadena(t, N0, tau_Bi, tau_Po)

indice_max = np.argmax(N_Po)
t_max_po   = t[indice_max]

# Máximo teórico: dN_Po/dt = 0  ->  t* = ln(tau_Po/tau_Bi) / (1/tau_Bi - 1/tau_Po)
t_max_po_teo = np.log(tau_Po / tau_Bi) / (1/tau_Bi - 1/tau_Po)

print(f"\n · Tiempo del máximo de Po (simulación) = {t_max_po:.2f} días")
print(f" · Tiempo del máximo de Po (teórico)    = {t_max_po_teo:.2f} días")

plt.figure(figsize=(9,6))

# Simulación

plt.plot(t, N_Bi, color='royalblue',  label="Bi (sim)")
plt.plot(t, N_Po, color='darkorange', label="Po (sim)")
plt.plot(t, N_Pb, color='seagreen',   label="Pb (sim)")

# Teórico

plt.plot(t, N_Bi_teo, '--', color='purple',  alpha=0.6, label="Bi (teórico)")
plt.plot(t, N_Po_teo, '--', color='yellow',  alpha=0.6, label="Po (teórico)")

plt.axvline(t_max_po,     linestyle=':',  color='black', label=f"Máx Po sim  t={t_max_po:.1f}")
plt.axvline(t_max_po_teo, linestyle='-.', color='gray',  label=f"Máx Po teo  t={t_max_po_teo:.1f}")

plt.xlabel("Tiempo (días)")
plt.ylabel("Número de núcleos")

plt.title("Cadena Bi-210 → Po-210 → Pb-208")
plt.legend(fontsize=8)

plt.grid(alpha=0.3)
plt.tight_layout()

plt.savefig("cadena.jpg", dpi=300, bbox_inches='tight')
plt.close()

# ============================================================
# 3. INFLUENCIA DEL NÚMERO DE NÚCLEOS (N0)
# ============================================================
print('\n=============================================================')
print("[3] INFLUENCIA DE N0: ")
print('=============================================================')

plt.figure(figsize=(8,5))

for N_test in [500, 2000, 5000]:
    
    t_test, N_sim_test = simulacion_desintegracion(N_test, tau_Bi, t_max2, pasos)
    plt.plot(t_test, N_sim_test / N_test, label=f"N0 = {N_test}")

# Curva teórica normalizada
t_ref = np.linspace(0, t_max2, 300)
plt.plot(t_ref, np.exp(-t_ref/tau_Bi), 'k--', label="Teórico")

print("\nSe observa que al aumentar N0 disminuye el ruido estadístico.")

plt.xlabel("Tiempo (días)")
plt.ylabel("N(t) / N0")

plt.title("Efecto del número de núcleos iniciales (normalizado)")
plt.legend()

plt.grid(alpha=0.3)
plt.tight_layout()

plt.savefig("N0.jpg", dpi=300, bbox_inches='tight')
plt.close()

# ============================================================
# 4. INFLUENCIA DEL MUESTREO TEMPORAL
# ============================================================
print('\n===================================================')
print("[4] INFLUENCIA DEL MUESTREO TEMPORAL")
print('===================================================')

plt.figure(figsize=(8,5))

for pasos_test in [10, 50, 150, 400]:
    
    t_test, N_sim_test = simulacion_desintegracion(N0, tau_Bi, t_max2, pasos_test)
    plt.plot(t_test, N_sim_test, label=f"pasos = {pasos_test}")

print("\nUn mayor número de pasos produce curvas más suaves.")

plt.xlabel("Tiempo (días)")
plt.ylabel("N(t)")

plt.title("Efecto del muestreo temporal")
plt.legend()

plt.grid(alpha=0.3)
plt.tight_layout()

plt.savefig("muestreo.jpg", dpi=300, bbox_inches='tight')
plt.close()

# ============================================================
# 5. FOTOMULTIPLICADOR
# ============================================================
print('\n==================================================================')
print("[5] FOTOMULTIPLICADOR")
print('==================================================================')

n_fotones_fm = 2000   # suficiente para buena estadística

# --- 5_opcional. Comparación método manual vs numpy ---
print("\n[5_opt] MÉTODO MANUAL DE POISSON vs NUMPY:")

nu_test   = 5
n_test    = 5000

muestra_manual = poisson_manual(nu_test, n_test)
muestra_numpy  = np.random.poisson(nu_test, n_test)

print(f" · Media manual = {np.mean(muestra_manual):.3f}  (teórico: {nu_test})")
print(f" · Media numpy  = {np.mean(muestra_numpy):.3f}  (teórico: {nu_test})")
print(f" · Std manual   = {np.std(muestra_manual):.3f}  (teórico: {np.sqrt(nu_test):.3f})")
print(f" · Std numpy    = {np.std(muestra_numpy):.3f}  (teórico: {np.sqrt(nu_test):.3f})")

bins = range(0, 20)
plt.figure(figsize=(8,5))
plt.hist(muestra_manual, bins=bins, alpha=0.6, label="Método manual", density=True, align='left')
plt.hist(muestra_numpy,  bins=bins, alpha=0.6, label="numpy",         density=True, align='left')

# Curva teórica
from scipy.stats import poisson as poisson_dist
x = np.arange(0, 20)
plt.plot(x, poisson_dist.pmf(x, nu_test), 'ko--', label=f"Teórico Poisson(ν={nu_test})")

plt.xlabel("n")
plt.ylabel("Probabilidad")
plt.title("Distribución de Poisson: método manual vs numpy")
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig("poisson_comparacion.jpg", dpi=300, bbox_inches='tight')
plt.close()

# --- 5a. Intensidad de la señal (ν=5 en todos los dínodos) ---
print("\n[5a] Intensidad de la señal (v=5, 6 dínodos, sin dínodo especial):")

resultados_base = fotomultiplicador(nu=5, n_fotones=n_fotones_fm)
media_base = np.mean(resultados_base)
std_base   = np.std(resultados_base)
ganancia_teorica = 5**6

print(f" · Electrones medios (sim)  = {media_base:.1f}")
print(f" · Desv. estándar           = {std_base:.1f}")
print(f" · Ganancia teórica (v^6)   = {ganancia_teorica}")

plt.figure(figsize=(8,5))

plt.hist(resultados_base, bins=50, edgecolor='black', color='steelblue', alpha=0.8)
plt.axvline(media_base, color='red', linestyle='--', label=f"Media = {media_base:.0f}")

plt.xlabel("Número de electrones")
plt.ylabel("Frecuencia")

plt.title("Distribución de electrones en el fotomultiplicador (ν=5)")
plt.legend()

plt.grid(alpha=0.3)
plt.tight_layout()

plt.savefig("fotomultiplicador_distribucion.jpg", dpi=300, bbox_inches='tight')
plt.close()

# --- 5b. Eficiencia del fotomultiplicador ---
print("\n[5b] Eficiencia del fotomultiplicador:")

umbral_ideal    = 1
umbral_realista = 25000

efic_ideal    = np.mean(resultados_base >= umbral_ideal)
efic_realista = np.mean(resultados_base >= umbral_realista)

print(f" · Eficiencia (umbral =       1 electrón) = {100*efic_ideal:.2f} %")
print(f" · Eficiencia (umbral = 25000 electrones) = {100*efic_realista:.2f} %")

# Curva de eficiencia frente al umbral
umbrales = np.logspace(0, 6, 200)
eficiencias = [np.mean(resultados_base >= u) for u in umbrales]

plt.figure(figsize=(8,5))
plt.plot(umbrales, eficiencias, color='steelblue')

plt.axvline(umbral_ideal,    color='green', linestyle='--', label=f"Umbral = 1  (ef={100*efic_ideal:.1f}%)")
plt.axvline(umbral_realista, color='red',   linestyle='--', label=f"Umbral = 25000 (ef={100*efic_realista:.1f}%)")

plt.xscale('log')
plt.xlabel("Umbral de electrones (escala log)")
plt.ylabel("Eficiencia")

plt.title("Eficiencia del fotomultiplicador vs umbral de detección")
plt.legend()

plt.grid(alpha=0.3)
plt.tight_layout()

plt.savefig("eficiencia_fotomultiplicador.jpg", dpi=300, bbox_inches='tight')
plt.close()

# --- 5c. Mejor dínodo para sustituir por ν=7 ---
print("\n[5c] Ganancia media según posición del dínodo especial (v=7):")

medias = [] 

for pos in range(6):
    
    res = fotomultiplicador(nu=5, n_fotones=n_fotones_fm, posicion_especial=pos, nu_especial=7)
    m   = np.mean(res)
    medias.append(m)
    
    print(f" · Posición {pos} -> media = {m:.1f}  (ganancia relativa = {m/media_base:.3f})")

# Calcular también las varianzas por posición
stds = []
for pos in range(6):
    res = fotomultiplicador(nu=5, n_fotones=n_fotones_fm, posicion_especial=pos, nu_especial=7)
    stds.append(np.std(res))

print("\n · Varianza relativa (std/media) por posición del dínodo especial:")
for pos, (m, s) in enumerate(zip(medias, stds)):
    print(f"   Posición {pos}: std/media = {s/m:.4f}")

print("\n · La ganancia MEDIA es idéntica en todas las posiciones.")
print("   Analíticamente: E[producto] = producto de E[Xi], independiente del orden.")
print("   La VARIANZA es menor cuando el dínodo especial está en la posición 0.")
print("   -> Lo óptimo es colocar el dínodo de v=7 al principio.")

# Gráfica de varianza por posición
plt.figure(figsize=(8,5))

plt.bar(range(6), [s/m for s, m in zip(stds, medias)], color='darkorange', edgecolor='black', alpha=0.8)

plt.xlabel("Posición del dínodo reemplazado (v=7)")
plt.ylabel("Varianza relativa (std/media)")

plt.title("Varianza relativa según posición del dínodo mejorado")

plt.xticks(range(6), [f"Dínodo {i}" for i in range(6)], rotation=15)
plt.grid(alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig("fotomultiplicador_varianza.jpg", dpi=300, bbox_inches='tight')

plt.close()

plt.figure(figsize=(8,5))

plt.bar(range(6), medias, color='steelblue', edgecolor='black', alpha=0.8)

plt.axhline(media_base, color='red', linestyle='--', label=f"Sin mejora = {media_base:.0f}")
plt.xlabel("Posición del dínodo reemplazado (v=7)")
plt.ylabel("Electrones medios")

plt.title("Optimización del fotomultiplicador: mejor posición para v=7")
plt.xticks(range(6), [f"Dínodo {i}" for i in range(6)], rotation=15)

plt.legend()
plt.grid(alpha=0.3, axis='y')
plt.tight_layout()

plt.savefig("fotomultiplicador_optimizacion.jpg", dpi=300, bbox_inches='tight')
plt.close()

print('\n==================================================================')
print("\nFin del programa.\n")
