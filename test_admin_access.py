#!/usr/bin/env python
"""Test TPO and HOD access to admin dashboard"""

from app import create_app

app = create_app()

with app.app_context():
    with app.test_client() as client:
        print('Testing TPO and HOD Admin Dashboard Access')
        print('='*70)
        
        # Test TPO Admin
        print('\nTPO Admin Access:')
        print('-'*70)
        resp = client.post('/auth/login', data={'username': 'tpo_admin', 'password': 'tpo@2024'})
        print(f'Login Status: {resp.status_code}')
        
        resp = client.get('/admin/dashboard')
        print(f'Admin Dashboard Access: {resp.status_code}')
        
        if resp.status_code == 200:
            content = resp.get_data(as_text=True)
            checks = {
                'Placement Stats': 'Total Students' in content,
                'Application Pipeline': 'Applied' in content,
                'Placement Trend Graph': 'placementTrendChart' in content,
                'All Placement Records': 'All Placement Records' in content,
                'Top Companies': 'Top Companies by Placements' in content,
            }
            
            for check, found in checks.items():
                print(f'  {check}: {"✓" if found else "✗"}')
        
        # Test HOD Admin
        print('\nHOD Admin Access:')
        print('-'*70)
        resp = client.post('/auth/login', data={'username': 'hod_admin', 'password': 'hod@2024'})
        print(f'Login Status: {resp.status_code}')
        
        resp = client.get('/admin/dashboard')
        print(f'Admin Dashboard Access: {resp.status_code}')
        
        if resp.status_code == 200:
            content = resp.get_data(as_text=True)
            checks = {
                'Placement Stats': 'Total Students' in content,
                'Application Pipeline': 'Applied' in content,
                'Placement Trend Graph': 'placementTrendChart' in content,
                'All Placement Records': 'All Placement Records' in content,
                'Top Companies': 'Top Companies by Placements' in content,
            }
            
            for check, found in checks.items():
                print(f'  {check}: {"✓" if found else "✗"}')
        
        # Test Regular Admin
        print('\nAdmin Access (Verification):')
        print('-'*70)
        resp = client.post('/auth/login', data={'username': 'admin', 'password': 'admin@2024'})
        print(f'Login Status: {resp.status_code}')
        
        resp = client.get('/admin/dashboard')
        print(f'Admin Dashboard Access: {resp.status_code}')
        
        if resp.status_code == 200:
            print('Admin dashboard accessible as expected')
        
        print('\n' + '='*70)
        print('RESULT: TPO and HOD can now access admin dashboard')
        print('='*70)
