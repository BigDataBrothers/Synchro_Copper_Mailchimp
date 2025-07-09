#!/usr/bin/env python3
"""
Script pour basculer entre mode TEST et PRODUCTION
"""

import os
import sys

def toggle_mode():
    """Bascule entre mode TEST et PRODUCTION"""
    sync_file = "sync.py"
    
    if not os.path.exists(sync_file):
        print("❌ Fichier sync.py non trouvé")
        return
    
    # Lire le fichier
    with open(sync_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Détecter le mode actuel
    if "TEST_MODE = True" in content:
        current_mode = "TEST"
        new_content = content.replace("TEST_MODE = True", "TEST_MODE = False")
        new_mode = "PRODUCTION"
    elif "TEST_MODE = False" in content:
        current_mode = "PRODUCTION"
        new_content = content.replace("TEST_MODE = False", "TEST_MODE = True")
        new_mode = "TEST"
    else:
        print("❌ Impossible de détecter le mode actuel")
        return
    
    # Demander confirmation
    print(f"🔄 Mode actuel: {current_mode}")
    print(f"🎯 Nouveau mode: {new_mode}")
    
    if new_mode == "PRODUCTION":
        print("⚠️  ATTENTION: Le mode PRODUCTION traitera TOUTE la base de données !")
        print("   Assurez-vous que c'est bien ce que vous voulez.")
    
    response = input("\n✅ Confirmer le changement ? (o/N): ").lower()
    
    if response in ['o', 'oui', 'y', 'yes']:
        # Écrire le fichier modifié
        with open(sync_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"✅ Mode basculé vers {new_mode}")
        print(f"📝 Fichier {sync_file} mis à jour")
        
        if new_mode == "PRODUCTION":
            print("🔥 RAPPEL: Vous êtes maintenant en mode PRODUCTION")
            print("   Tous les contacts seront traités !")
        else:
            print("🧪 Mode TEST activé - seuls les emails @exemple seront traités")
    else:
        print("❌ Changement annulé")

if __name__ == "__main__":
    toggle_mode()
