"""
Diagram Generator - Convert Mermaid code to PNG images
Uses mermaid.py library for conversion
100% FREE - No API costs
"""
import os
import sys
import base64
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from mermaid import Mermaid
    MERMAID_AVAILABLE = True
except ImportError:
    MERMAID_AVAILABLE = False
    print("⚠️ mermaid.py not installed. Install with: pip install mermaid.py")

from engine.logger import logger


class DiagramGenerator:
    """Generate diagrams from Mermaid code"""
    
    def __init__(self, output_dir: str = "Generated_Images"):
        """
        Initialize diagram generator
        
        Args:
            output_dir: Directory to save generated images
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        logger.info(f"📁 Diagram output directory: {self.output_dir}")
    
    def generate_png(self, mermaid_code: str, filename: Optional[str] = None) -> Optional[str]:
        """
        Convert Mermaid code to PNG image
        
        Args:
            mermaid_code: Mermaid diagram code
            filename: Optional custom filename
            
        Returns:
            Path to generated PNG file, or None if failed
        """
        if not MERMAID_AVAILABLE:
            logger.error("❌ mermaid.py library not available")
            return None
        
        try:
            # Generate filename
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"diagram_{timestamp}.png"
            
            # Ensure .png extension
            if not filename.endswith('.png'):
                filename = filename + '.png'
            
            output_path = self.output_dir / filename
            
            # Clean mermaid code (remove markdown code blocks if present)
            clean_code = self._clean_mermaid_code(mermaid_code)
            
            # Generate diagram
            logger.info(f"🎨 Generating diagram: {filename}")
            logger.debug(f"Mermaid code: {clean_code[:200]}...")
            
            mermaid = Mermaid(clean_code)
            mermaid.to_png(str(output_path))
            
            if output_path.exists():
                file_size = output_path.stat().st_size
                logger.info(f"✅ Diagram generated: {filename} ({file_size} bytes)")
                return str(output_path)
            else:
                logger.error(f"❌ Diagram file not created: {filename}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Diagram generation failed: {e}")
            return None
    
    def _clean_mermaid_code(self, code: str) -> str:
        """
        Clean Mermaid code (remove markdown code blocks)
        
        Args:
            code: Raw Mermaid code (may include ```mermaid blocks)
            
        Returns:
            Clean Mermaid code
        """
        # Remove markdown code blocks
        if code.startswith('```mermaid'):
            code = code[10:]  # Remove ```mermaid
        if code.startswith('```'):
            code = code[3:]  # Remove ```
        if code.endswith('```'):
            code = code[:-3]  # Remove trailing ```
        
        return code.strip()
    
    def encode_image(self, image_path: str) -> str:
        """
        Encode image to base64 (for API uploads)
        
        Args:
            image_path: Path to image file
            
        Returns:
            Base64 encoded image string
        """
        try:
            with open(image_path, "rb") as img_file:
                encoded = base64.b64encode(img_file.read()).decode('utf-8')
            logger.debug(f"📦 Encoded image: {image_path}")
            return encoded
        except Exception as e:
            logger.error(f"❌ Image encoding failed: {e}")
            return ""
    
    def generate_flowchart(self, title: str, nodes: list, edges: list) -> str:
        """
        Generate flowchart Mermaid code
        
        Args:
            title: Chart title
            nodes: List of (id, label, color) tuples
            edges: List of (from_id, to_id) tuples
            
        Returns:
            Mermaid code string
        """
        code = f"graph TD\n"
        
        # Add nodes with styles
        for node_id, label, color in nodes:
            code += f'    {node_id}["{label}"]\n'
            code += f'    style {node_id} fill:{color},color:#fff,stroke:#333,stroke-width:2px\n'
        
        # Add edges
        for from_id, to_id in edges:
            code += f'    {from_id} --> {to_id}\n'
        
        return code
    
    def generate_sequence(self, participants: list, messages: list) -> str:
        """
        Generate sequence diagram Mermaid code
        
        Args:
            participants: List of (id, label) tuples
            messages: List of (from_id, to_id, message) tuples
            
        Returns:
            Mermaid code string
        """
        code = "sequenceDiagram\n"
        
        # Add participants
        for pid, label in participants:
            code += f'    participant {pid} as {label}\n'
        
        # Add messages
        for from_id, to_id, message in messages:
            code += f'    {from_id}->>{to_id}: {message}\n'
        
        return code
    
    def generate_mindmap(self, root: str, branches: list) -> str:
        """
        Generate mind map Mermaid code
        
        Args:
            root: Central topic
            branches: List of branch strings
            
        Returns:
            Mermaid code string
        """
        code = "mindmap\n"
        code += f'  root(({root}))\n'
        
        for branch in branches:
            code += f'    {branch}\n'
        
        return code


# Pre-built diagram templates for common use cases
class DiagramTemplates:
    """Pre-built diagram templates for common scenarios"""
    
    @staticmethod
    def three_tier_architecture() -> str:
        """Three-tier architecture diagram"""
        return """
graph TD
    A["🖥️ Client Layer<br/>Browser/Mobile App"] --> B["⚙️ Application Layer<br/>Business Logic/API"]
    B --> C["💾 Data Layer<br/>Database/Storage"]
    C --> D[("🗄️ Database")]
    B --> E[("🚀 Cache")]
    
    style A fill:#3498db,color:#fff,stroke:#2980b9,stroke-width:2px
    style B fill:#e74c3c,color:#fff,stroke:#c0392b,stroke-width:2px
    style C fill:#2ecc71,color:#fff,stroke:#27ae60,stroke-width:2px
    style D fill:#27ae60,color:#fff,stroke:#1e8449,stroke-width:2px
    style E fill:#f39c12,color:#fff,stroke:#d35400,stroke-width:2px
"""
    
    @staticmethod
    def lead_generation_workflow() -> str:
        """Lead generation workflow diagram"""
        return """
graph LR
    A["📘 Facebook Lead"] --> B["🤖 AI Processing"]
    B --> C["📊 Lead Scoring"]
    C --> D["✅ Hot Lead<br/>Score ≥ 80"]
    C --> E["⏳ Warm Lead<br/>Score 50-79"]
    D --> F["📩 Email Notification"]
    D --> G["💬 WhatsApp Alert"]
    D --> H["📝 Odoo CRM"]
    E --> I["📧 Nurture Campaign"]
    
    style A fill:#1877F2,color:#fff,stroke:#0d5b99,stroke-width:2px
    style B fill:#9b59b6,color:#fff,stroke:#8e44ad,stroke-width:2px
    style C fill:#f39c12,color:#fff,stroke:#d35400,stroke-width:2px
    style D fill:#2ecc71,color:#fff,stroke:#27ae60,stroke-width:2px
    style E fill:#f39c12,color:#fff,stroke:#d35400,stroke-width:2px
    style F fill:#3498db,color:#fff,stroke:#2980b9,stroke-width:2px
    style G fill:#25D366,color:#fff,stroke:#128C7E,stroke-width:2px
    style H fill:#e74c3c,color:#fff,stroke:#c0392b,stroke-width:2px
    style I fill:#95a5a6,color:#fff,stroke:#7f8c8d,stroke-width:2px
"""
    
    @staticmethod
    def ai_automation_pipeline() -> str:
        """AI automation pipeline diagram"""
        return """
sequenceDiagram
    participant U as 👤 User
    participant D as 📊 Dashboard
    participant A as 🤖 AI Engine
    participant O as 📝 Odoo
    participant S as 📱 Social Media
    
    U->>D: Create Task
    D->>A: Generate Content
    A-->>D: Professional Text
    D->>O: Create Approval
    O-->>U: Awaiting Approval
    U->>O: Approve Task
    O->>S: Execute Action
    S-->>U: Task Complete
"""
    
    @staticmethod
    def marketing_funnel() -> str:
        """Marketing funnel diagram"""
        return """
graph TD
    A["👥 Awareness<br/>Top of Funnel"] --> B["💡 Interest<br/>Consideration"]
    B --> C["🎯 Evaluation<br/>Middle of Funnel"]
    C --> D["💰 Purchase<br/>Bottom of Funnel"]
    D --> E["❤️ Loyalty<br/>Retention"]
    E --> F["📣 Advocacy<br/>Referrals"]
    
    style A fill:#f39c12,color:#fff,stroke:#d35400,stroke-width:2px
    style B fill:#e67e22,color:#fff,stroke:#d35400,stroke-width:2px
    style C fill:#e74c3c,color:#fff,stroke:#c0392b,stroke-width:2px
    style D fill:#2ecc71,color:#fff,stroke:#27ae60,stroke-width:2px
    style E fill:#3498db,color:#fff,stroke:#2980b9,stroke-width:2px
    style F fill:#9b59b6,color:#fff,stroke:#8e44ad,stroke-width:2px
"""
    
    @staticmethod
    def mvc_architecture() -> str:
        """MVC architecture diagram"""
        return """
graph LR
    A["👤 User"] --> B["📱 View<br/>UI/Presentation"]
    B --> C["🎮 Controller<br/>Business Logic"]
    C --> D["🗂️ Model<br/>Data/Database"]
    D --> C
    C --> B
    B --> A
    
    style A fill:#9b59b6,color:#fff,stroke:#8e44ad,stroke-width:2px
    style B fill:#3498db,color:#fff,stroke:#2980b9,stroke-width:2px
    style C fill:#e74c3c,color:#fff,stroke:#c0392b,stroke-width:2px
    style D fill:#2ecc71,color:#fff,stroke:#27ae60,stroke-width:2px
"""
    
    @staticmethod
    def ci_cd_pipeline() -> str:
        """CI/CD pipeline diagram"""
        return """
graph LR
    A["💻 Code Commit"] --> B["🔄 CI Pipeline"]
    B --> C["🧪 Automated Tests"]
    C --> D["📦 Build Artifact"]
    D --> E["🚀 Deploy to Staging"]
    E --> F["✅ Manual Testing"]
    F --> G["🌐 Production Deploy"]
    
    style A fill:#3498db,color:#fff,stroke:#2980b9,stroke-width:2px
    style B fill:#f39c12,color:#fff,stroke:#d35400,stroke-width:2px
    style C fill:#e74c3c,color:#fff,stroke:#c0392b,stroke-width:2px
    style D fill:#9b59b6,color:#fff,stroke:#8e44ad,stroke-width:2px
    style E fill:#1abc9c,color:#fff,stroke:#16a085,stroke-width:2px
    style F fill:#f39c12,color:#fff,stroke:#d35400,stroke-width:2px
    style G fill:#2ecc71,color:#fff,stroke:#27ae60,stroke-width:2px
"""


# Test the diagram generator
if __name__ == "__main__":
    print("=" * 60)
    print("🎨 Testing Diagram Generator")
    print("=" * 60)
    
    # Initialize generator
    generator = DiagramGenerator()
    
    # Test 1: Generate three-tier architecture
    print("\n📊 Test 1: Three-Tier Architecture")
    mermaid_code = DiagramTemplates.three_tier_architecture()
    img_path = generator.generate_png(mermaid_code, "test_three_tier.png")
    if img_path:
        print(f"✅ Generated: {img_path}")
    else:
        print("❌ Generation failed - mermaid.py may not be installed")
        print("💡 Install with: pip install mermaid.py")
    
    # Test 2: Generate lead workflow
    print("\n📊 Test 2: Lead Generation Workflow")
    mermaid_code = DiagramTemplates.lead_generation_workflow()
    img_path = generator.generate_png(mermaid_code, "test_lead_workflow.png")
    if img_path:
        print(f"✅ Generated: {img_path}")
    
    # Test 3: Generate marketing funnel
    print("\n📊 Test 3: Marketing Funnel")
    mermaid_code = DiagramTemplates.marketing_funnel()
    img_path = generator.generate_png(mermaid_code, "test_marketing_funnel.png")
    if img_path:
        print(f"✅ Generated: {img_path}")
    
    print("\n" + "=" * 60)
    print("✅ Diagram Generator Tests Complete!")
    print("=" * 60)
    print("\n📁 Check Generated_Images/ folder for output files")
    print("💡 If tests failed, install mermaid.py:")
    print("   pip install mermaid.py")
