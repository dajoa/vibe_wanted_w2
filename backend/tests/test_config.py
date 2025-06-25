import pytest
import os
from unittest.mock import patch
from app.config import Config


class TestConfiguration:
    """설정 및 환경 관리 테스트"""
    
    def test_config_module_exists(self):
        """config.py 모듈이 존재하는지 확인"""
        from app.config import settings
        assert settings is not None
        
    def test_config_has_required_attributes(self):
        """설정 객체가 필수 속성들을 가지고 있는지 확인"""
        from app.config import settings
        
        # 필수 설정 속성들
        required_attrs = [
            "fastapi_host",
            "fastapi_port", 
            "langsmith_api_key",
            "environment"
        ]
        
        for attr in required_attrs:
            assert hasattr(settings, attr), f"설정에 {attr} 속성이 없습니다"
            
    def test_default_values(self):
        """기본값이 올바르게 설정되어 있는지 확인"""
        from app.config import settings
        
        # 기본값 확인
        assert settings.fastapi_host == "localhost"
        assert settings.fastapi_port == 8000
        assert settings.environment == "development"
        
    @patch.dict(os.environ, {
        "FASTAPI_HOST": "0.0.0.0",
        "FASTAPI_PORT": "9000",
        "LANGSMITH_API_KEY": "test_key_123",
        "ENVIRONMENT": "production"
    })
    def test_environment_variable_override(self):
        """환경 변수로 설정을 오버라이드할 수 있는지 확인"""
        # config 모듈을 다시 임포트하여 환경 변수 반영
        import importlib
        from app import config
        importlib.reload(config)
        
        assert config.settings.fastapi_host == "0.0.0.0"
        assert config.settings.fastapi_port == 9000
        assert config.settings.langsmith_api_key == "test_key_123"
        assert config.settings.environment == "production"
        
    def test_config_class_exists(self):
        """Settings 클래스가 존재하는지 확인"""
        from app.config import Settings
        assert Settings is not None
        
    def test_settings_is_instance_of_settings_class(self):
        """settings가 Settings 클래스의 인스턴스인지 확인"""
        from app.config import Settings, settings
        assert isinstance(settings, Settings)
        
    def test_config_validation(self):
        """설정 검증이 올바르게 작동하는지 확인"""
        from app.config import settings
        
        # 포트는 정수여야 함
        assert isinstance(settings.fastapi_port, int)
        assert 1 <= settings.fastapi_port <= 65535
        
        # 호스트는 문자열이어야 함
        assert isinstance(settings.fastapi_host, str)
        assert len(settings.fastapi_host) > 0

    def test_config_has_required_attributes(self):
        """Test config has all required attributes"""
        config = Config()
        
        assert hasattr(config, 'GOOGLE_API_KEY')
        assert hasattr(config, 'LANGSMITH_API_KEY')
        assert hasattr(config, 'LANGSMITH_PROJECT')
        
    def test_config_loads_from_env(self):
        """Test config loads from environment variables"""
        # Set test environment variables
        os.environ['GOOGLE_API_KEY'] = 'test_google_key'
        os.environ['LANGSMITH_API_KEY'] = 'test_langsmith_key'
        os.environ['LANGSMITH_PROJECT'] = 'test_project'
        
        config = Config()
        
        assert config.GOOGLE_API_KEY == 'test_google_key'
        assert config.LANGSMITH_API_KEY == 'test_langsmith_key'
        assert config.LANGSMITH_PROJECT == 'test_project'
        
        # Clean up
        del os.environ['GOOGLE_API_KEY']
        del os.environ['LANGSMITH_API_KEY'] 
        del os.environ['LANGSMITH_PROJECT']


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 