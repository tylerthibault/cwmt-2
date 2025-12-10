"""
MJML Service Module

Handles conversion of MJML markup to responsive HTML for email templates.
MJML is a markup language designed to reduce the complexity of coding responsive emails.

This module provides utilities to:
- Convert MJML-like syntax to responsive HTML
- Provide email-safe HTML templates
- Handle conversion errors gracefully

Note: This is a simplified MJML converter that handles common components.
For full MJML features, install Node.js MJML CLI separately.
"""
from flask import current_app
import re


class MJMLService:
    """Service for handling MJML to HTML conversion"""
    
    @staticmethod
    def mjml_to_html(mjml_content):
        """
        Convert MJML markup to responsive HTML.
        Uses a simplified converter for common MJML components.
        
        Args:
            mjml_content (str): MJML markup string
        
        Returns:
            dict: {
                'success': bool,
                'html': str (if success),
                'error': str (if failure)
            }
        
        Example:
            result = MJMLService.mjml_to_html('<mjml><mj-body>...</mj-body></mjml>')
            if result['success']:
                html = result['html']
        """
        if not mjml_content or not mjml_content.strip():
            return {
                'success': False,
                'error': 'MJML content is empty'
            }
        
        try:
            # Extract body content
            body_match = re.search(r'<mj-body[^>]*>(.*?)</mj-body>', mjml_content, re.DOTALL)
            if not body_match:
                return {
                    'success': False,
                    'error': 'MJML must contain <mj-body> element'
                }
            
            body_content = body_match.group(1)
            
            # Get background color from mj-body
            bg_color_match = re.search(r'background-color=["\']([^"\']+)["\']', mjml_content)
            body_bg = bg_color_match.group(1) if bg_color_match else '#f4f4f4'
            
            # Start building HTML
            html_parts = []
            
            # Email-safe DOCTYPE and structure
            html_parts.append('<!DOCTYPE html>')
            html_parts.append('<html xmlns="http://www.w3.org/1999/xhtml">')
            html_parts.append('<head>')
            html_parts.append('<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />')
            html_parts.append('<meta name="viewport" content="width=device-width, initial-scale=1.0"/>')
            html_parts.append('</head>')
            html_parts.append(f'<body style="margin: 0; padding: 0; background-color: {body_bg};">')
            html_parts.append('<table border="0" cellpadding="0" cellspacing="0" width="100%">')
            html_parts.append('<tr>')
            html_parts.append('<td align="center" style="padding: 20px 0;">')
            
            # Convert sections
            html_parts.append(MJMLService._convert_sections(body_content))
            
            html_parts.append('</td>')
            html_parts.append('</tr>')
            html_parts.append('</table>')
            html_parts.append('</body>')
            html_parts.append('</html>')
            
            return {
                'success': True,
                'html': '\n'.join(html_parts)
            }
            
        except Exception as e:
            current_app.logger.error(f"MJML conversion error: {str(e)}")
            return {
                'success': False,
                'error': f'MJML conversion failed: {str(e)}'
            }
    
    @staticmethod
    def _convert_sections(content):
        """Convert mj-section elements to HTML tables"""
        html_parts = []
        
        # Find all sections
        sections = re.findall(r'<mj-section([^>]*)>(.*?)</mj-section>', content, re.DOTALL)
        
        for attrs, section_content in sections:
            # Extract section attributes
            bg_color = MJMLService._extract_attr(attrs, 'background-color', '#ffffff')
            padding = MJMLService._extract_attr(attrs, 'padding', '20px')
            
            # Start section table
            html_parts.append(f'<table border="0" cellpadding="0" cellspacing="0" width="600" style="background-color: {bg_color}; max-width: 600px;">')
            html_parts.append('<tr>')
            html_parts.append(f'<td style="padding: {padding};">')
            
            # Convert columns
            html_parts.append(MJMLService._convert_columns(section_content))
            
            html_parts.append('</td>')
            html_parts.append('</tr>')
            html_parts.append('</table>')
        
        return '\n'.join(html_parts)
    
    @staticmethod
    def _convert_columns(content):
        """Convert mj-column elements to HTML"""
        html_parts = []
        
        # Find all columns
        columns = re.findall(r'<mj-column([^>]*)>(.*?)</mj-column>', content, re.DOTALL)
        
        if not columns:
            # No columns, treat entire content as single column
            return MJMLService._convert_components(content)
        
        # Create table for columns
        html_parts.append('<table border="0" cellpadding="0" cellspacing="0" width="100%">')
        html_parts.append('<tr>')
        
        for attrs, column_content in columns:
            html_parts.append('<td style="vertical-align: top;">')
            html_parts.append(MJMLService._convert_components(column_content))
            html_parts.append('</td>')
        
        html_parts.append('</tr>')
        html_parts.append('</table>')
        
        return '\n'.join(html_parts)
    
    @staticmethod
    def _convert_components(content):
        """Convert mj-* components to HTML"""
        html_parts = []
        
        # Convert mj-text
        texts = re.findall(r'<mj-text([^>]*)>(.*?)</mj-text>', content, re.DOTALL)
        for attrs, text_content in texts:
            font_size = MJMLService._extract_attr(attrs, 'font-size', '16px')
            color = MJMLService._extract_attr(attrs, 'color', '#000000')
            font_family = MJMLService._extract_attr(attrs, 'font-family', 'Arial, sans-serif')
            font_weight = MJMLService._extract_attr(attrs, 'font-weight', 'normal')
            align = MJMLService._extract_attr(attrs, 'align', 'left')
            
            html_parts.append(f'<p style="font-size: {font_size}; color: {color}; font-family: {font_family}; font-weight: {font_weight}; text-align: {align}; margin: 10px 0;">{text_content.strip()}</p>')
        
        # Convert mj-button
        buttons = re.findall(r'<mj-button([^>]*)>(.*?)</mj-button>', content, re.DOTALL)
        for attrs, button_text in buttons:
            bg_color = MJMLService._extract_attr(attrs, 'background-color', '#007bff')
            color = MJMLService._extract_attr(attrs, 'color', '#ffffff')
            href = MJMLService._extract_attr(attrs, 'href', '#')
            
            html_parts.append(f'<table border="0" cellpadding="0" cellspacing="0" style="margin: 20px 0;">')
            html_parts.append('<tr>')
            html_parts.append('<td align="center">')
            html_parts.append(f'<a href="{href}" style="background-color: {bg_color}; color: {color}; padding: 12px 24px; text-decoration: none; border-radius: 4px; display: inline-block; font-family: Arial, sans-serif; font-size: 16px;">{button_text.strip()}</a>')
            html_parts.append('</td>')
            html_parts.append('</tr>')
            html_parts.append('</table>')
        
        # Convert mj-divider
        dividers = re.findall(r'<mj-divider([^>]*)/?>(?:</mj-divider>)?', content)
        for attrs in dividers:
            border_color = MJMLService._extract_attr(attrs, 'border-color', '#cccccc')
            html_parts.append(f'<hr style="border: none; border-top: 1px solid {border_color}; margin: 20px 0;" />')
        
        # Convert mj-image
        images = re.findall(r'<mj-image([^>]*)/?>(?:</mj-image>)?', content)
        for attrs in images:
            src = MJMLService._extract_attr(attrs, 'src', '')
            alt = MJMLService._extract_attr(attrs, 'alt', '')
            width = MJMLService._extract_attr(attrs, 'width', 'auto')
            
            if src:
                html_parts.append(f'<img src="{src}" alt="{alt}" style="max-width: {width}; height: auto; display: block; margin: 10px 0;" />')
        
        return '\n'.join(html_parts)
    
    @staticmethod
    def _extract_attr(attrs_string, attr_name, default=''):
        """Extract attribute value from attribute string"""
        pattern = rf'{attr_name}=["\']([^"\']+)["\']'
        match = re.search(pattern, attrs_string)
        return match.group(1) if match else default
    
    @staticmethod
    def validate_mjml(mjml_content):
        """
        Validate MJML syntax.
        
        Args:
            mjml_content (str): MJML markup string
        
        Returns:
            dict: {
                'valid': bool,
                'errors': list (if invalid)
            }
        """
        # Basic validation - check for required tags
        if not mjml_content or not mjml_content.strip():
            return {
                'valid': False,
                'errors': ['MJML content is empty']
            }
        
        # Check for <mjml> wrapper
        if '<mjml>' not in mjml_content.lower():
            return {
                'valid': False,
                'errors': ['MJML must be wrapped in <mjml> tags']
            }
        
        # Check for <mj-body>
        if '<mj-body>' not in mjml_content.lower():
            return {
                'valid': False,
                'errors': ['MJML must contain <mj-body> element']
            }
        
        # Try converting to validate
        result = MJMLService.mjml_to_html(mjml_content)
        
        if result['success']:
            return {
                'valid': True
            }
        else:
            return {
                'valid': False,
                'errors': [result['error']]
            }
    
    @staticmethod
    def get_starter_template(template_type='basic'):
        """
        Get a starter MJML template.
        
        Args:
            template_type (str): Type of template (basic, button, welcome, etc.)
        
        Returns:
            str: MJML template string
        """
        templates = {
            'basic': '''<mjml>
  <mj-body>
    <mj-section>
      <mj-column>
        <mj-text font-size="20px" color="#626262" font-family="Helvetica">
          Hello {user_name}!
        </mj-text>
        <mj-text font-size="16px" color="#525252">
          This is a basic email template. Replace this text with your content.
        </mj-text>
      </mj-column>
    </mj-section>
  </mj-body>
</mjml>''',
            
            'button': '''<mjml>
  <mj-body background-color="#f4f4f4">
    <mj-section background-color="#ffffff" padding="20px">
      <mj-column>
        <mj-text font-size="20px" color="#626262" font-family="Helvetica">
          Hello {user_name}!
        </mj-text>
        <mj-text font-size="16px" color="#525252">
          Please click the button below to continue.
        </mj-text>
        <mj-button background-color="#007bff" color="#ffffff" href="{action_link}">
          Click Here
        </mj-button>
      </mj-column>
    </mj-section>
  </mj-body>
</mjml>''',
            
            'welcome': '''<mjml>
  <mj-body background-color="#f4f4f4">
    <mj-section background-color="#ffffff" padding="20px">
      <mj-column>
        <mj-text font-size="24px" color="#007bff" font-family="Helvetica" font-weight="bold" align="center">
          Welcome to {app_name}!
        </mj-text>
        <mj-divider border-color="#007bff"></mj-divider>
        <mj-text font-size="16px" color="#525252">
          Hello {user_name},
        </mj-text>
        <mj-text font-size="16px" color="#525252">
          We're excited to have you join us! Your account has been successfully created.
        </mj-text>
        <mj-button background-color="#007bff" color="#ffffff" href="{login_link}">
          Get Started
        </mj-button>
        <mj-text font-size="14px" color="#999999" align="center">
          © {year} {app_name}. All rights reserved.
        </mj-text>
      </mj-column>
    </mj-section>
  </mj-body>
</mjml>''',
            
            'reset_password': '''<mjml>
  <mj-body background-color="#f4f4f4">
    <mj-section background-color="#ffffff" padding="20px">
      <mj-column>
        <mj-text font-size="20px" color="#626262" font-family="Helvetica">
          Password Reset Request
        </mj-text>
        <mj-text font-size="16px" color="#525252">
          Hello {user_name},
        </mj-text>
        <mj-text font-size="16px" color="#525252">
          We received a request to reset your password. Click the button below to create a new password.
        </mj-text>
        <mj-button background-color="#dc3545" color="#ffffff" href="{reset_link}">
          Reset Password
        </mj-button>
        <mj-text font-size="14px" color="#999999">
          This link will expire in {expiry_time}.
        </mj-text>
        <mj-text font-size="14px" color="#999999">
          If you didn't request this, please ignore this email.
        </mj-text>
      </mj-column>
    </mj-section>
  </mj-body>
</mjml>'''
        }
        
        return templates.get(template_type, templates['basic'])
