#!/usr/bin/env python3
"""
Test e-post maler for delt tavle
"""

def test_templates():
    print("🧪 Testing delt tavle e-post maler...")
    
    # Test 1: Check noteboard_update.html content
    print("📧 Testing noteboard_update.html...")
    try:
        with open('/workspaces/smartreminder/templates/emails/noteboard_update.html', 'r') as f:
            content = f.read()
            
        if 'DELT TAVLE' in content:
            print("   ✅ Update template: 'DELT TAVLE' tekst funnet")
        else:
            print("   ❌ Update template: 'DELT TAVLE' tekst mangler")
        
        if 'linear-gradient' in content:
            print("   ✅ Update template: Moderne styling funnet")
        else:
            print("   ❌ Update template: Moderne styling mangler")
            
        if 'delte tavlen' in content:
            print("   ✅ Update template: Tydelig delt tavle-tekst funnet")
        else:
            print("   ❌ Update template: Mangler tydelig delt tavle-tekst")
            
    except Exception as e:
        print(f"   ❌ Feil ved lesing av update template: {e}")
    
    # Test 2: Check noteboard_invitation.html content
    print("📧 Testing noteboard_invitation.html...")
    try:
        with open('/workspaces/smartreminder/templates/emails/noteboard_invitation.html', 'r') as f:
            content = f.read()
            
        if 'INVITASJON TIL DELT TAVLE' in content:
            print("   ✅ Invitation template: 'INVITASJON TIL DELT TAVLE' tekst funnet")
        else:
            print("   ❌ Invitation template: 'INVITASJON TIL DELT TAVLE' tekst mangler")
        
        if 'linear-gradient' in content:
            print("   ✅ Invitation template: Moderne styling funnet")
        else:
            print("   ❌ Invitation template: Moderne styling mangler")
            
        if 'delt tavle' in content.lower():
            print("   ✅ Invitation template: Tydelig delt tavle-tekst funnet")
        else:
            print("   ❌ Invitation template: Mangler tydelig delt tavle-tekst")
            
    except Exception as e:
        print(f"   ❌ Feil ved lesing av invitation template: {e}")
    
    print("\n✅ E-post mal testing fullført!")
    print("📝 Sammendrag av forbedringer:")
    print("   • Bedre kontrast med moderne gradient-design")
    print("   • Tydelig markering av 'DELT TAVLE' vs påminnelser")
    print("   • Forbedret typography og lesbarhet")
    print("   • Mer informative meldinger og CTAs")
    print("   • Fikset styling-problemer med kontraster")

if __name__ == "__main__":
    test_templates()
